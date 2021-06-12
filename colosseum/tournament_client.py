import socket
import json
import gym
from utils.socket_wrap import SocketWrapper
from utils.compress import decompress
from envs.envs_list import make_test_env, all_environments


# Send JSON through socket
def send_json(sock, data):
    return sock.sendall(json.dumps(data).encode("utf-8"))


# Receive JSON from socket
def recv_json(sock):
    return sock.recv(2 ** 30)  # Arbitrarily large buffer


class NetworkEnv(gym.Env):
    def __init__(self, env_id, seed, game_ip, game_port, username, token):
        print("Host: {}:{}".format(game_ip, game_port))
        self.game_connection = SocketWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        # Create game server connection
        self.game_connection.connect((game_ip, game_port))
        send_json(self.game_connection, {"username": username, "token": token})
        self.game_data = recv_json(self.game_connection)
        self.terminated = self.game_data["type"] == "terminate"

        # Create env for initial action and observation spaces
        self.env = make_test_env(env_id, seed=seed)
        self.agent = agent = (
            self.game_data["agent"] if not self.terminated else self.env.agents[0]
        )
        self.observation_space = self.env.observation_spaces[agent]
        self.action_space = self.env.action_spaces[agent]
        self.action_space.seed(seed)
        self.obs = None

    def step(self, action):
        if self.terminated:
            print("terminated before single step occurred!")
            return self.obs, 0, True, {}

        # Send action to game server
        act_data = {"type": "action", "action": action}
        send_json(self.game_connection, act_data)

        # Receive observation from game server
        observation_data = recv_json(self.game_connection)
        done = False
        if observation_data["type"] != "observation":
            # Game is done
            rew = 0
            done = True
            info = {}
            info["_terminated"] = True
            return self.obs, rew, done, info

        # Unpack observation
        obs = decompress(observation_data["data"][self.agent])
        self.obs = obs

        # TODO: Decide what information a live tournament agent should have access to.
        # Probably observation, info, done, though done is obvious from the message type
        rew = 0
        info = {}
        return obs, rew, done, info

    def render(self, mode='human'):
        # TODO: Figure out appropriate behavior here. Probably rendering live on the website.
        return self.env.render(mode=mode)

    def reset(self):
        "Resetting mid-game would cause serious desync issues"
        return

    def close(self):
        self.env.close()
        self.game_connection.close()


# Local environment used to test if agent works before connecting to network env
class TestEnv(gym.Env):
    def __init__(self, env_id):
        seed = 1
        self.env = make_test_env(env_id, seed=seed)
        self.env.reset()
        self.agent = agent = self.env.agents[0]
        self.observation_space = self.env.observation_spaces[agent]
        self.action_space = self.env.action_spaces[agent]
        self.num_steps = 0
        self.was_done = False

    def reset(self):
        obss = self.env.reset()
        self.num_steps = 0
        self.was_done = False
        return obss[self.agent]

    def step(self, action):
        assert not self.was_done, "stepped after done, should terminate loop"
        # Set random actions for all other agents
        actions = {
            agent: self.env.action_spaces[agent].sample() for agent in self.env.agents
        }
        actions[self.agent] = action
        obss, rews, dones, infos = self.env.step(actions)

        if self.num_steps > 50:
            done = True
        else:
            done = dones[self.agent]

        obs = obss[self.agent]
        rew = rews[self.agent]
        info = infos[self.agent]

        self.was_done = done
        self.num_steps += 1

        return obs, rew, done, info

    def render(self, mode='human'):
        return


class TournamentConnection:
    def __init__(self, ip, port, username, password, available_games):
        print("Connecting to matchmaker for following games: ", available_games)
        if available_games == ["__all__"]:
            print("TESTING ALL GAMES")
            available_games = list(all_environments.keys())

        self.username = username
        self.ip_address = ip
        self.port = port
        self.username = username
        self.password = password
        self.available_games = available_games
        self.main_connection = None  # Connection to tournament server
        self._test_environments()

    # Test agent in every game
    def _test_environments(self):
        for game in self.available_games:
            test_env = TestEnv(game)
            test_env.reset()
            for _ in range(100):
                action = test_env.action_space.sample()
                _, _, done, _ = test_env.step(action)
                if done:
                    print("{} passed test in {}".format(self.username, game))
                    break

    def _connect_game_server(self):
        # Receive game server info from matchmaker
        ready_data = recv_json(self.main_connection)
        print(ready_data)
        send_json(self.main_connection, {"type": "ready"})

        # Receive game server info from matchmaker
        sdata = recv_json(self.main_connection)
        print(sdata)

        # Create network env with game server info
        env = NetworkEnv(
            sdata["env"],
            sdata["seed"],
            self.ip_address,
            sdata["port"],
            self.username,
            sdata["token"],
        )
        return env

    # Start connection to matchmaking server
    def _setup_main_connection(self):
        self.main_connection = SocketWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        self.main_connection.connect((self.ip_address, self.port))
        send_json(
            self.main_connection,
            {
                "username": self.username,
                "password": self.password,
                "client_version": "1.0",
                "available_games": self.available_games,
            },
        )
        init_data = recv_json(self.main_connection)

        # Handle connection errors
        if init_data["type"] == "bad_creds":
            raise RuntimeError("server did not accept credentials")
        if init_data["type"] == "bad_client_version":
            raise RuntimeError(
                "Old client version. Please udpate your client to the latest version available."
            )
        if init_data["type"] == "connected_too_many_servers":
            raise RuntimeError(
                "This username is already connected to the server too many times."
            )
        if init_data["type"] != "connect_success":
            raise RuntimeError("Something went wrong during login.")

    # TODO: Implement terminate signal for tournament and receive it here
    def next_match(self):
        # Create tournament server connection if it does not already exist
        if self.main_connection is None:
            self._setup_main_connection()

        # Connect to game server
        game_env = self._connect_game_server()
        self.main_connection.close()
        self.main_connection = None
        return game_env
