#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from .game_client import MatchmakerConnection


class ColosseumAgent:
    def __init__(self, latency=0,  games=["__all__"], port=12345, direct=False, host="localhost"):
        self.host = host
        self.port = port
        self.username = ''
        self.password = ''
        self.latency = latency
        self.direct = direct
        self.games = games
        self.env = None

    def connect(self, username, password):
        self.username = username
        self.password = password
        mm_env = MatchmakerConnection(
                self.host, self.port, self.username, self.password, available_games=self.games
                )
        self.env = mm_env.start_new()

    def run(self):
        for i in range(100000):
            if i % 100 == 0:
                print("Timestep {}".format(i))
            time.sleep(self.latency / 1000)  # Used to simulate network latency
            action = self.env.action_space.sample()  # Choose a random action
            obs, rew, done, info = self.env.step(action)  # Send action to game server
            if done:
                print("Done")
                break  # Episode ended
