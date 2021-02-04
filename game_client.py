import socket
import json
import sys
import time
import gym
import threading
import numpy as np
from colosseum.utils.socket_wrap import SocketWrapper
from colosseum.utils.compress import decompress
from colosseum.envs.envs_list import make_test_env, all_environments


def send_json(socket, data):
    return socket.sendall(json.dumps(data).encode("utf-8"))


def recv_json(socket):
    return socket.recv(2 ** 30)


class SingConnectEnv(gym.Env):
    def __init__(self, env_id, seed, game_ip, game_port, username, token):
        print(game_ip, game_port)
        self.game_connection = SocketWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        self.game_connection.connect((game_ip, game_port))
        send_json(self.game_connection, {"username": username, "token": token})
        self.game_data = recv_json(self.game_connection)
        self.terminated = self.game_data["type"] == "terminate"
        self.env = make_test_env(env_id, seed=seed)
        self.agent = agent = (
            self.game_data["agent"] if not self.terminated else self.env.agents[0]
        )
        self.observation_space = self.env.observation_spaces[agent]
        self.action_space = self.env.action_spaces[agent]
        self.action_space.seed(seed)

        # print(self.agent)
        # exit(0)
        self.num_steps = 0

    def reset(self):
        self.num_steps = 0
        self.obs = self.env.reset()[self.agent]
        return self.obs

    def step(self, action):
        if self.terminated:
            print("terminated before single step occurred!")
            return self.obs, 0, True, {}
        print("Action: {}".format(action))
        act_data = {"type": "action", "action": action}
        print("act_data: {}".format(act_data))
        send_json(self.game_connection, act_data)
        observation_data = recv_json(self.game_connection)
        done = False
        if observation_data["type"] != "observation":
            if observation_data["type"] == "game_end":
                print(observation_data["score"])
            rew = 0
            done = True
            info = {}
            info["_terminated"] = True
            print("terminated")
            return self.obs, done

        obs = decompress(observation_data["data"][self.agent])
        self.obs = obs
        # self.obs = obs = obss[self.agent]
        # done = dones[self.agent]
        # rew = rews[self.agent]
        # info = infos[self.agent]

        # info["_terminated"] = done
        self.num_steps += 1

        # return obs, rew, done, info
        rew = 0
        info = {}
        return obs, rew, done, info

    def render(self):
        return self.env.render()

    def close(self):
        self.env.close()
        self.game_connection.close()


class TestEnv(gym.Env):
    def __init__(self, env_id):
        seed = 1
        self.env = make_test_env(env_id, seed=seed)
        self.agent = agent = self.env.agents[0]
        self.observation_space = self.env.observation_spaces[agent]
        self.action_space = self.env.action_spaces[agent]

    def reset(self):
        obss = self.env.reset()
        self.num_steps = 0
        self.was_done = False
        return obss[self.agent]

    def step(self, action):
        assert not self.was_done, "stepped after done, should terminate loop"
        other_actions = {
            agent: self.env.action_spaces[agent].sample() for agent in self.env.agents
        }
        other_actions[self.agent] = action
        obss, rews, dones, infos = self.env.step(other_actions)

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


class LeaderboardConnection:
    def __init__(self, ip, port, username, password, available_games):
        print("LEADERBOARD: ", available_games)
        if available_games == ["__all__"]:
            print("TESTING ALL GAMES")
            available_games = list(all_environments.keys())
        self.username = username
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.available_games = available_games
        self.main_connection = None
        self.test_env_idx = 0
        self._test_environments()

    def _test_environments(self):
        for game in self.available_games:
            test_env = TestEnv(game)
            test_env.reset()
            for i in range(100):
                obs, rew, done, info = test_env.step(test_env.action_space.sample())
                if done:
                    print("Succesfully ran {}".format(game))
                    break

    def _create_new_tcp_env(self):
        # tell main server that we are ready to be matched
        send_json(self.main_connection, {"type": "ready"})

        sdata = recv_json(self.main_connection)
        # time.sleep(2)
        env = SingConnectEnv(
            sdata["env"],
            sdata["seed"],
            self.ip,
            sdata["port"],
            self.username,
            sdata["token"],
        )
        # Use this to test game server directly
        # env = SingConnectEnv(sdata['env'],sdata['seed'],self.ip, 35011,self.username,"A4C1B65BCE1D6EA4")
        return env

    def setup_tcp_connection(self):
        self.main_connection = SocketWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        )
        self.main_connection.connect((self.ip, self.port))
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

        if init_data["type"] == "bad_creds":
            raise RuntimeError("server did not accept credentials")
        elif init_data["type"] == "bad_client_version":
            raise RuntimeError(
                "Old client version. Please udpate your client to the latest version available."
            )
        elif init_data["type"] == "connected_too_many_servers":
            raise RuntimeError(
                "This username is already connected to the server too many times."
            )
        elif init_data["type"] != "connect_success":
            raise RuntimeError("Something went wrong during login.")

    def start_new(self):
        if self.main_connection is None:
            self.setup_tcp_connection()
        return self._create_new_tcp_env()
