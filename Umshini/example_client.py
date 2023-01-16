#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import traceback
from .tournament_client import TournamentConnection
from colorama import Fore, Style
from halo import Halo


class ColosseumTournamentAgent:
    def __init__(self, policy, latency=0,  games=["__all__"], port=12345,
                 direct=False, host="localhost", maximum_rounds=10000, debug=False):
        self.host = host
        self.policy = policy
        self.port = port
        self.botname = ''
        self.key = ''
        self.latency = latency
        self.direct = direct
        self.games = games
        self.tournament = None
        self.maximum_rounds = maximum_rounds
        self.debug = debug

    def connect(self, botname, key):
        self.botname = botname
        self.key = key
        try:
            # TODO: Use policy for test
            # Test that policy runs without errors in local environments
            self.tournament = TournamentConnection(
                self.host, self.port, self.botname, self.key,
                available_games=self.games, debug=self.debug
            )
            print(Fore.GREEN + "Bot: {}'s policy has passed environment verifications".format(self.botname))
            print(Style.RESET_ALL)
        except Exception:
            print(Fore.RED + "Bot: {}'s policy has failed verification testing in environment: ".format(self.botname))
            print(Style.RESET_ALL)
            quit()

    def run(self):
        # Connect to tournament server each round, until the end signal is received.
        try:
            env = self.tournament.next_match()
            if self.debug:
                print(env)
        except Exception as e:
            print(Fore.RED + str(e))
            if self.debug:
                print(traceback.format_exc())
            print(Style.RESET_ALL)
            quit()
        current_round = 1
        while env is not None:
            surprises = []
            term = False
            trunc = False
            timestep = 0
            rew = info = None
            obs = env.reset()
            while not (term or trunc):
                if timestep % 100 == 0 and self.debug:
                    print(f"{self.botname}: Timestep {timestep}\n")
                time.sleep(self.latency / 1000)  # Used to simulate network latency
                (action, surprise) = self.policy(obs, rew, term, trunc, info)  # receive action and surprise from user
                obs, rew, term, trunc, info = env.step(action)  # Send action to game server
                surprises.append(surprise)  # Collect surprise for later use when game server supports
                timestep += 1
            print(Fore.GREEN + f"Round {current_round} complete")
            print(Style.RESET_ALL)
            current_round += 1
            if current_round > self.maximum_rounds:
                env = None
            else:
                env = self.tournament.next_match()
