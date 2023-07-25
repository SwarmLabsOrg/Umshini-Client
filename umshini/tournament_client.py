# pyright: reportGeneralTypeIssues=false, reportUnboundVariable=false, reportOptionalMemberAccess=false
import json
import socket

import gymnasium as gym
import numpy as np
from colorama import Fore, Style
from halo import Halo

from umshini.envs import ALL_ENVIRONMENTS, make_test_env
from umshini.utils.compress import decompress
from umshini.utils.socket_wrap import SocketWrapper


# Send JSON through socket
def send_json(sock, data):
    return sock.sendall(json.dumps(data).encode("utf-8"))


# Receive JSON from socket
def recv_json(sock, timeout=60):
    sock.settimeout(timeout)
    data = sock.recv(2**30)  # Arbitrarily large buffer
    sock.settimeout(60)
    return data


class NetworkEnv(gym.Env):
    def __init__(self, env_id, seed, game_ip, game_port, username, token, verbose=0):
        self.verbose = verbose
        if self.verbose > 0:
            print(f"Host: {game_ip}:{game_port}")
        self.game_connection = SocketWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        # Create game server connection
        self.game_connection.connect((game_ip, game_port))
        send_json(self.game_connection, {"username": username, "token": token})
        self.game_data = recv_json(self.game_connection)
        self.terminated = self.game_data["type"] == "terminate"

        # Create env for initial action and observation spaces
        self.env, self.turn_based = make_test_env(env_id, seed=seed)
        if self.verbose > 1:
            print("Game server data:", self.game_data)
        self.agent = (
            self.game_data["agent"]
            if not self.terminated
            else self.env.possible_agents[0]
        )
        self.observation_space = self.env.observation_space(self.agent)
        self.action_space = self.env.action_space(self.agent)
        self.action_space.seed(seed)
        self.obs = None

    def step(self, action_surprise):
        if self.terminated:
            print("terminated before single step occurred!")
            return self.obs, 0, True, True, {}
        if type(action_surprise) is tuple:
            action = action_surprise[0]
            surprise = action_surprise[1]
        else:
            action = action_surprise
            surprise = 0.0
        # Convert Numpy types to Python types
        if hasattr(action, "dtype"):
            action = action.item()

        # Send action to game server
        assert (
            isinstance(action, int)
            or isinstance(action, float)
            or isinstance(action, str)
            or isinstance(action, dict)
            or isinstance(action, list)
        ), "Action is not a valid type."
        assert self.action_space.contains(action), "Action not in action space."
        assert isinstance(surprise, int) or isinstance(
            surprise, float
        ), "Surprise is not a valid type."

        act_data = {"type": "action", "action": action, "surprise": surprise}
        if self.verbose > 1:
            print("sending action")
        send_json(self.game_connection, act_data)
        if self.verbose > 1:
            print("sent action")

        # Receive observation from game server
        if self.verbose > 1:
            print("receiving obs")
        observation_data = recv_json(self.game_connection)
        if self.verbose > 1:
            print("received obs")
        if observation_data["type"] != "observation":
            # Game is done
            rew = 0
            term = True
            trunc = True
            info = {}
            info["_terminated"] = True
            self.spinner.succeed()
            return self.obs, rew, term, trunc, info

        # Unpack observation
        obs = decompress(observation_data["data"][self.agent])
        self.obs = obs
        info = decompress(observation_data["info"][self.agent])
        self.info = info

        # TODO: Decide what information a live tournament agent should have access to.
        # Probably observation, info, term or trunc, though term or trunc are obvious from the message type
        rew = 0
        term = False
        trunc = False
        self.steps += 1
        self.spinner.text = f"Playing game (step: {self.steps})"
        return obs, rew, term, trunc, info

    def render(self, mode="human"):
        # TODO: Figure out appropriate behavior here. Probably rendering live on the website.
        return self.env.render(mode=mode)

    def reset(self):
        self.steps = 0
        self.spinner = Halo(
            text=f"Playing game (step: {self.steps})",
            text_color="cyan",
            color="green",
            spinner="dots",
        )
        self.spinner.start()
        # Get initial observation
        if self.verbose > 1:
            print("receiving initial obs")
        observation_data = recv_json(self.game_connection)
        if self.verbose > 1:
            print("received initial obs")
            print(observation_data)
            if not observation_data:
                print("No data received")
        if observation_data["type"] != "observation":
            # Game is done
            return self.obs

        # Unpack observation
        obs = decompress(observation_data["data"][self.agent])
        info = decompress(observation_data["info"][self.agent])
        self.obs = obs
        self.info = info
        return self.obs, self.info

    def close(self):
        self.env.close()
        self.game_connection.close()


# Local environment used to test if agent works before connecting to network env
class TestEnv(gym.Env):
    def __init__(self, env_id):
        seed = 1
        self.env, self.turn_based = make_test_env(env_id, seed=seed, debug=True)
        self.env.reset()
        self.agent = agent = self.env.agents[0]
        self.observation_space = self.env.observation_space(agent)
        self.action_space = self.env.action_space(agent)
        self.num_steps = 0
        self.was_term = False
        self.was_trunc = False
        self.obss = None

    def reset(self):
        self.num_steps = 0
        self.was_term = False
        self.was_trunc = False
        obss, info = self.env.reset()
        return obss, info

    def step(self, action):
        assert (
            not self.was_term and not self.was_trunc
        ), "stepped after term or trunc, should terminate loop"
        # Set random actions for all other agents in parallel game or None in turn-based game
        actions = {
            agent: (None if self.turn_based else self.env.action_space(agent).sample())
            for agent in self.env.agents
        }
        actions[self.env.aec_env.agent_selection] = action
        self.obss, rews, terms, truncs, infos = self.env.step(actions)

        if self.num_steps > 50:
            trunc = True
            term = True
        else:
            term = terms[self.agent]
            trunc = truncs[self.agent]

        obs = self.obss[self.agent]
        rew = rews[self.agent]
        info = infos[self.agent]

        self.was_term = term
        self.was_trunc = trunc
        self.num_steps += 1

        # Find next active agents
        if self.turn_based:
            active_agents = [self.env.unwrapped.agent_selection]
        else:
            active_agents = self.env.agents

        # Step again if testing agent is not next
        if not self.was_term and not self.was_trunc and self.agent not in active_agents:
            obs = self.obss[self.env.unwrapped.agent_selection]
            if isinstance(obs, dict) and "action_mask" in obs:
                legal_mask = obs["action_mask"]
                legal_actions = legal_mask.nonzero()[0]
                action = np.random.choice(legal_actions)
            else:
                action = self.env.action_space(
                    self.env.unwrapped.agent_selection
                ).sample()
            return self.step(action)
        else:
            return obs, rew, term, trunc, info

    def render(self, mode="human"):
        return


# Local environment used to test if agent works before connecting to network env
class TestAECEnv(gym.Env):
    def __init__(self, env_id):
        seed = 1
        self.env = make_test_env(env_id, seed=seed, debug=True)
        self.env.reset()
        self.agent = agent = self.env.agents[0]
        self.observation_space = self.env.observation_spaces[agent]
        self.action_space = self.env.action_spaces[agent]
        self.num_steps = 0
        self.was_term = False
        self.was_trunc = False

    def reset(self):
        self.num_steps = 0
        self.was_term = False
        self.was_trunc = False
        self.env.reset()

    def step(self, action):
        assert (
            not self.was_term and not self.was_trunc
        ), "stepped after term or trunc, should terminate loop"
        # Set random actions for all other agents
        self.env.step(action)
        if self.num_steps > 50:
            trunc = True
            term = True
        else:
            obs, rew, term, trunc, info = self.env.last()

        self.was_term = term
        self.was_trunc = trunc
        self.num_steps += 1

    def last(self):
        return self.env.last()

    def render(self, mode="human"):
        return


class TournamentConnection:
    def __init__(self, ip, port, botname, key, available_games, debug=False):
        # Initialize class variables
        self.botname = botname
        self.ip_address = ip
        self.port = int(port)
        self.key = key
        self.main_connection = None  # Connection to tournament server
        self.tournament_completed = False
        self.debug = debug
        # Grab all available games
        if self.debug:
            print("Connecting to matchmaker for following games: ", available_games)
        if available_games == ["__all__"]:
            if self.debug:
                print("TESTING ALL GAMES")
            available_games = list(ALL_ENVIRONMENTS.keys())
        # Initialize available games
        # Test agent in every game
        self.available_games = available_games
        self.current_match = 0
        self._test_environments()

    # Test agent in every game
    def _test_environments(self):
        for game in self.available_games:
            test_env = TestEnv(game)
            obs, info = test_env.reset()
            for i in range(100):
                if (
                    obs is not None
                    and isinstance(obs, dict)
                    and obs
                    and "action_mask" in obs
                ):
                    action = np.random.choice(obs["action_mask"].nonzero()[0])
                else:
                    action = test_env.action_space.sample()
                obs, _, term, trunc, _ = test_env.step(action)
                if term or trunc:
                    if self.debug:
                        print(f"{self.botname} passed test in {game}")
                    break

    def _connect_game_server(self):
        # If tournament is over, return no environment
        if self.tournament_completed:
            return None

        # Receive game server info from matchmaker
        spinner = Halo(
            text="Waiting for players", text_color="cyan", color="green", spinner="dots"
        )
        spinner.start()
        try:
            ready_data = recv_json(self.main_connection, timeout=60)
        except TimeoutError as err:
            print("Not enough players to start tournament.", flush=True)
            raise err
        spinner.succeed()

        if self.debug:
            print(ready_data)
        send_json(self.main_connection, {"type": "ready"})

        # Receive game server info from matchmaker
        spinner = Halo(
            text="Creating your game", text_color="cyan", color="green", spinner="dots"
        )
        spinner.start()
        try:
            sdata = recv_json(self.main_connection)
            while sdata.get("queued") is True:
                sdata = recv_json(self.main_connection)
        except TimeoutError as err:
            print("Failed to receive game info from server", flush=True)
            raise err
        spinner.succeed()

        # Create network env with game server info
        env = NetworkEnv(
            sdata["env"],
            sdata["seed"],
            self.ip_address,
            sdata["port"],
            sdata["username"],
            sdata["token"],
        )
        return env

    # Start connection to matchmaking server
    def _setup_main_connection(self):
        self.main_connection = SocketWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        try:
            self.main_connection.connect((self.ip_address, self.port))
        except ConnectionRefusedError:
            raise RuntimeError("Tournament server is offline.")

        send_json(
            self.main_connection,
            {
                "botname": self.botname,
                "key": self.key,
                "client_version": "1.0",
                "available_games": self.available_games,
            },
        )

        try:
            init_data = recv_json(self.main_connection)
        except TimeoutError:
            raise RuntimeError("Failed to connect to matchmaker.")
        except json.decoder.JSONDecodeError:
            raise RuntimeError("Server returned an invalid response.")

        # Handle connection errors
        if init_data["type"] == "malformed_creds":
            raise RuntimeError("Credentials were formatted incorrectly")
        if init_data["type"] == "bad_creds":
            raise RuntimeError("server did not accept credentials")
        if init_data["type"] == "bad_client_version":
            raise RuntimeError(
                "Old client version. Please update your client to the latest version available."
            )
        if init_data["type"] == "connected_too_many_servers":
            raise RuntimeError(
                "This user is already connected to the server too many times."
            )
        if init_data["type"] == "invalid_botname":
            raise RuntimeError(
                f"This user does not have a bot with the provided name ({self.botname})"
            )
        if init_data["type"] != "connect_success":
            raise RuntimeError(
                f"Something went wrong during login: {init_data['type']}"
            )

        # Check if tournament is complete
        if init_data["complete"]:
            self.tournament_completed = True

    def next_match(self):
        if self.current_match > 0:
            spinner = Halo(
                text="Waiting for next round",
                text_color="cyan",
                color="green",
                spinner="dots",
            )
            spinner.start()

        # Create tournament server connection if it does not already exist
        if self.main_connection is None:
            try:
                self._setup_main_connection()
            except Exception as e:
                raise e

        if self.current_match > 0:
            spinner.succeed()

        if self.tournament_completed:
            print(Fore.GREEN + f"Bot: {self.botname} successfully completed tournament")
        elif self.current_match == 0:
            # Connect to game server
            print(Fore.GREEN + f"Bot: {self.botname} successfully connected to Umshini")
            pass
        print(Style.RESET_ALL)

        # Connect to game server
        game_env = self._connect_game_server()
        self.main_connection.close()
        self.main_connection = None
        self.current_match = 1
        return game_env
