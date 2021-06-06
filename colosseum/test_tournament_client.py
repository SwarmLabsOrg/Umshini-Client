#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from .tournament_client import TournamentConnection


class ColosseumTournamentAgent:
    def __init__(self, latency=0,  games=["__all__"], port=12345, direct=False, host="localhost"):
        self.host = host
        self.port = port
        self.username = ''
        self.password = ''
        self.latency = latency
        self.direct = direct
        self.games = games
        self.tournament = None

    def connect(self, username, password):
        self.username = username
        self.password = password
        self.tournament = TournamentConnection(
            self.host, self.port, self.username, self.password, available_games=self.games
        )

    def run(self):
        # Connect to tournament server for each round, until and end signal is received.
        env = self.tournament.next_match()
        while env is not None:
            done = False
            timestep = 0
            while not done:
                if timestep % 100 == 0:
                    print(f"{self.username}: Timestep {timestep}")
                time.sleep(self.latency / 1000)  # Used to simulate network latency
                action = env.action_space.sample()  # Choose a random action
                obs, rew, done, info = env.step(action)  # Send action to game server
                timestep += 1
            env = self.tournament.next_match()
