#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import numpy as np
from .tournament_client import TournamentConnection


class ColosseumTournamentAgent:
    def __init__(self, latency=0,  games=["__all__"], port=12345, direct=False, host="localhost", maximum_rounds=10000):
        self.host = host
        self.port = port
        self.username = ''
        self.password = ''
        self.latency = latency
        self.direct = direct
        self.games = games
        self.tournament = None
        self.maximum_rounds = maximum_rounds

    def connect(self, username, password):
        self.username = username
        self.password = password
        self.tournament = TournamentConnection(
            self.host, self.port, self.username, self.password, available_games=self.games
        )

    def run(self):
        # Connect to tournament server for each round, until and end signal is received.
        print("running")
        env = self.tournament.next_match()
        current_round = 1
        while env is not None:
            obs = None
            done = False
            timestep = 0
            while not done:
                if timestep % 100 == 0:
                    print(f"{self.username}: Timestep {timestep}")
                time.sleep(self.latency / 1000)  # Used to simulate network latency
                if (obs is not None
                       and isinstance(obs, dict)
                       and obs and "action_mask" in obs
                       and any(obs["action_mask"] == 1)):
                    action = np.random.choice(obs["action_mask"].nonzero()[0])
                else:
                    action = env.action_space.sample()  # Choose a random action
                if (isinstance(action, np.int64)):
                    action = int(action)
                obs, rew, done, info = env.step(action)  # Send action to game server
                timestep += 1
            current_round += 1
            if current_round > self.maximum_rounds:
                env = None
            else:
                env = self.tournament.next_match()

