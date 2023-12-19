# pyright: reportGeneralTypeIssues=false, reportUnboundVariable=false, reportOptionalMemberAccess=false, reportIncompatibleMethodOverride=false
import json
import socket

import gymnasium as gym
import numpy as np
from colorama import Fore, Style
from halo import Halo

from umshini.envs import ALL_ENVIRONMENTS, make_parallel_env
from umshini.utils.compress import decompress
from umshini.utils.socket_wrap import SocketWrapper


# Send JSON through socket
def send_json(sock, data):
    return sock.sendall(json.dumps(data).encode("utf-8"))


# Receive JSON from socket
def recv_json(sock, timeout=180):
    sock.settimeout(timeout)
    data = sock.recv(2**30)  # Arbitrarily large buffer
    sock.settimeout(180)
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
        self.default = self.game_data["type"] == "default"
        if self.default:
            print(Fore.GREEN + "Opponent didn't connect, win by default.")
            return

        # Create env for initial action and observation spaces
        self.env, self.turn_based = make_parallel_env(env_id, seed=seed)
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
        self.observation = None

    def step(self, action_surprise):
        if self.terminated:
            print("terminated before single step occurred!")
            return self.observation, 0, True, True, {}
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
        assert self.action_space.contains(
            action
        ), f"Action not in action space.\nAction: {action}.\nSpace: {self.action_space}"
        assert isinstance(surprise, int) or isinstance(
            surprise, float
        ), "Surprise is not a valid type."
        if isinstance(action, str):
            action = action.replace("{", "")
            action = action.replace("}", "")
        act_data = {"type": "action", "action": action, "surprise": surprise}
        if self.verbose > 1:
            print("sending action")
        send_json(self.game_connection, act_data)
        if self.verbose > 1:
            print("sent action")

        # Receive observation from game server
        if self.verbose > 1:
            print("receiving obs")
        try:
            observation_data = recv_json(self.game_connection)
        except Exception as e:
            self.spinner.stop()
            print(Fore.YELLOW + "Environment terminated prematurely! Round drawn.")
            if self.verbose:
                print(e)
            return self.observation, 0, True, True, {}
        if self.verbose > 1:
            print("received obs")
        if observation_data["type"] != "observation":
            # Game is done
            reward = 0
            termination = True
            truncation = True
            info = {}
            info["_terminated"] = True
            self.spinner.succeed()
            if (
                observation_data["type"] == "game_end"
                and observation_data.get("scores") is not None
            ):
                scores = observation_data.get("scores")
                print(Fore.GREEN + f"Scores: {str(scores)}")
                winners = []
                max_score = -10000
                for bot, score in scores.items():
                    if score > max_score:
                        max_score = score
                        winners = [bot]
                    elif score == max_score:
                        winners.append(bot)
                if len(winners) == 1:
                    print(Fore.GREEN + "Winner: " + winners[0])
                elif len(winners) > 1:
                    print(Fore.GREEN + "Draw between " + " and ".join(winners))
            return self.observation, reward, termination, truncation, info

        # Unpack observation
        observation = decompress(observation_data["data"][self.agent])
        self.observation = observation
        info = decompress(observation_data["info"][self.agent])
        self.info = info

        # TODO: Decide what information a live tournament agent should have access to.
        # Probably observation, info, termination or truncation, though termination or truncation are obvious from the message type
        reward = 0
        termination = False
        truncation = False
        self.steps += 1
        self.spinner.text = f"Playing game (step: {self.steps})"
        return observation, reward, termination, truncation, info

    def render(self, mode="human"):
        return self.env.render(mode=mode)

    def reset(self, **kwargs):
        self.steps = 0
        # Get initial observation
        if self.verbose > 1:
            print("receiving initial obs")
        observation_data = recv_json(self.game_connection)
        if self.verbose > 1:
            print("received initial observation")
            print(observation_data)
            if not observation_data:
                print("No data received")
        if observation_data["type"] != "observation":
            # Game is done
            return self.observation

        # Unpack observation
        observation = decompress(observation_data["data"][self.agent])
        info = decompress(observation_data["info"][self.agent])
        self.observation = observation
        self.info = info
        try:
            meta = json.loads(observation_data.get("meta"))
            if meta.get("botnames") is not None and isinstance(
                meta.get("botnames"), list
            ):
                print(Fore.GREEN + "Playing " + " vs. ".join(meta.get("botnames")))
        except Exception as e:
            if self.verbose:
                print(e)
            pass

        self.spinner = Halo(
            text=f"Playing game (step: {self.steps})",
            text_color="cyan",
            color="green",
            spinner="dots",
        )
        self.spinner.start()

        return self.observation, self.info

    def close(self):
        self.env.close()
        self.game_connection.close()


# Local environment used to test if agent works before connecting to network env
class TestEnv(gym.Env):
    def __init__(self, env_id):
        seed = 1
        self.env, self.turn_based = make_parallel_env(env_id, seed=seed, debug=True)
        self.env.reset()
        self.agent = agent = self.env.agents[0]
        self.observation_space = self.env.observation_space(agent)
        self.action_space = self.env.action_space(agent)
        self.num_steps = 0
        self.was_terminated = False
        self.was_truncated = False
        self.observations = None

    def reset(self, **kwargs):
        self.num_steps = 0
        self.was_terminated = False
        self.was_truncated = False
        observations, infos = self.env.reset()
        return observations, infos

    def step(self, action):
        assert (
            not self.was_terminated and not self.was_truncated
        ), "stepped after termination or truncation, should terminate loop"
        # Set random actions for all other agents in parallel game or None in turn-based game
        actions = {
            agent: (None if self.turn_based else self.env.action_space(agent).sample())
            for agent in self.env.agents
        }
        actions[self.env.aec_env.agent_selection] = action
        self.observations, rewards, terminations, truncations, infos = self.env.step(
            actions
        )

        if self.num_steps > 50:
            truncation = True
            termination = True
        else:
            termination = terminations[self.agent]
            truncation = truncations[self.agent]

        observation = self.observations[self.agent]
        reward = rewards[self.agent]
        info = infos[self.agent]

        self.was_terminated = termination
        self.was_truncated = truncation
        self.num_steps += 1

        # Find next active agents
        if self.turn_based:
            active_agents = [self.env.unwrapped.agent_selection]
        else:
            active_agents = self.env.agents

        # Step again if testing agent is not next
        if (
            not self.was_terminated
            and not self.was_truncated
            and self.agent not in active_agents
        ):
            observation = self.observations[self.env.unwrapped.agent_selection]
            if isinstance(observation, dict) and "action_mask" in observation:
                legal_mask = observation["action_mask"]
                legal_actions = legal_mask.nonzero()[0]
                action = np.random.choice(legal_actions)
            else:
                action = self.env.action_space(
                    self.env.unwrapped.agent_selection
                ).sample()
            return self.step(action)
        else:
            return observation, reward, termination, truncation, info

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
        self.round_number = 1
        self._test_environments()

    # Test agent in every game
    def _test_environments(self):
        for game in self.available_games:
            test_env = TestEnv(game)
            observation, info = test_env.reset()
            for i in range(100):
                if (
                    observation is not None
                    and isinstance(observation, dict)
                    and observation
                    and "action_mask" in observation
                ):
                    action = np.random.choice(observation["action_mask"].nonzero()[0])
                else:
                    action = test_env.action_space.sample()
                observation, _, termination, truncation, _ = test_env.step(action)
                if termination or truncation:
                    if self.debug:
                        print(f"{self.botname} passed test in {game}")
                    break

    def _connect_game_server(self):
        # If tournament is over, return no environment
        if self.tournament_completed:
            return None, {}

        # Receive game server info from matchmaker
        spinner = Halo(
            text="Waiting for players", text_color="cyan", color="green", spinner="dots"
        )
        spinner.start()
        try:
            ready_data = recv_json(self.main_connection, timeout=600)
        except TimeoutError as err:
            print("Not enough players to start tournament.", flush=True)
            raise err
        spinner.succeed()

        if self.debug:
            print(ready_data)

        if ready_data.get("type") == "bye":
            return None, {"bye": True}

        if ready_data.get("type") == "reconnect":
            # shortcut to reconnect
            sdata = ready_data
            env = NetworkEnv(
                sdata["env"],
                sdata["seed"],
                self.ip_address,
                sdata["port"],
                sdata["username"],
                sdata["token"],
            )
            return env, {}

        send_json(self.main_connection, {"type": "ready"})

        # Receive game server info from matchmaker
        spinner = Halo(
            text="Creating your game", text_color="cyan", color="green", spinner="dots"
        )
        spinner.start()
        try:
            sdata = recv_json(self.main_connection)
            if sdata.get("type") == "default":
                spinner.stop()
                print(Fore.GREEN + "Opponent didn't connect, win by default.")
                return None, {"default": True}
            if sdata.get("type") == "bye":
                spinner.stop()
                return None, {"bye": True}
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
        return env, {}

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
        if init_data["type"] == "duplicate_registration":
            raise RuntimeError("This user is already registered in this tournament.")
        if init_data["type"] != "connect_success":
            raise RuntimeError(
                f"Something went wrong during login: {init_data['type']}"
            )
        self.round_number = init_data.get("round_number", 1)
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
        game_env, info = self._connect_game_server()
        self.main_connection.close()
        self.main_connection = None
        self.current_match = 1
        info["round_number"] = self.round_number
        return game_env, info
