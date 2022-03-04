#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from .tournament_client import TournamentConnection
from colorama import Fore, Style

class ColosseumTournamentAgent:
    def __init__(self, policy, latency=0,  games=["__all__"], port=12345, direct=False, host="localhost", maximum_rounds=10000):
        self.host = host
        self.policy = policy
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
        try:
            #change this so policy is used for test
            #connection to server isn't here, just policy test
            self.tournament = TournamentConnection(
                self.host, self.port, self.username, self.password, available_games=self.games
            )
            print(Fore.GREEN + "User: {}'s policy has passed environment verifications".format(self.username))
        except:
            print(Fore.RED + "User: {}'s policy has failed verification testing in environment: ".format(self.username))
            quit()
    def run(self):
        # Connect to tournament server for each round, until and end signal is received.
        # connection to server (that can fail) is here
        try:
            env = self.tournament.next_match()
            print(Fore.GREEN + "User: {} successfully connected to Umshini".format(self.username))
        except Exception as e:
            print(Fore.RED + e)
            quit()
        current_round = 1
        while env is not None:
            surprise = []
            done = False
            timestep = 0
            obs, rew, info = None
            while not done:
                if timestep % 100 == 0:
                    print(f"{self.username}: Timestep {timestep}")
                time.sleep(self.latency / 1000)  # Used to simulate network latency
                (action, surprise) = self.policy(obs, rew, done, info)  # recieve action and surprise from user
                obs, rew, done, info = env.step(action)  # Send action to game server
                surprise.append(surprise) # Collect surprise for later use when game server supports
                timestep += 1
            current_round += 1
            if current_round > self.maximum_rounds:
                env = None
            else:
                env = self.tournament.next_match()

