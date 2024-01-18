#!/usr/bin/env python3
# pyright: reportOptionalMemberAccess=false, reportGeneralTypeIssues=false
import threading

import numpy as np
import time
import traceback

from colorama import Fore, Style
from multiprocessing import TimeoutError
from multiprocessing.pool import ThreadPool

from umshini import ALL_ENVIRONMENTS
from umshini.tournament_client import TournamentConnection
from umshini.utils.validate_action import validate_action

TURN_LIMIT = 20  # seconds

class UmshiniTournamentAgent:

    def __init__(
        self,
        policy,
        latency=0,
        games=["__all__"],
        port=12345,
        direct=False,
        host="localhost",
        maximum_rounds=10000,
        debug=False,
        role=None,
    ):
        self.host = host
        self.policy = policy
        self.port = port
        self.botname = ""
        self.key = ""
        self.latency = latency
        self.direct = direct
        self.games = games
        self.tournament = None
        self.maximum_rounds = maximum_rounds
        self.debug = debug
        self.role = role
        self.num_turns = 0
        self.num_default = 0

    def connect(self, botname, key):
        self.botname = botname
        self.key = key

        # Environment verification
        if any(game not in ALL_ENVIRONMENTS for game in self.games):
            print(
                Fore.RED
                + f"Environment name invalid: {self.games}. Available environments: {ALL_ENVIRONMENTS}."
            )
            print(Style.RESET_ALL)
            quit()

        try:
            # TODO: Use policy for test
            # Test that policy runs without errors in local environments
            self.tournament = TournamentConnection(
                self.host,
                self.port,
                self.botname,
                self.key,
                role=self.role,
                available_games=self.games,
                debug=self.debug,
            )
        except Exception as e:
            if self.debug:
                print(Fore.RED + f"ERROR: {e}")
            print(
                Fore.RED
                + f"Bot: {self.botname}'s policy has failed verification testing in {self.games[-1]} [{self.policy.__name__}]"
            )
            print(Style.RESET_ALL)
            quit()

    def run(self):
        # Connect to tournament server each round, until the end signal is received.
        envs = None
        try:
            envs, match_info = self.tournament.next_match()
            if self.debug:
                print(envs)
        except Exception as e:
            print(Fore.RED + str(e))
            if self.debug:
                print(traceback.format_exc())
            print(Style.RESET_ALL)
            match_info = {}
            quit()
        self.current_round = int(match_info.get("round_number", 1))
        while (
            envs is not None
            or match_info.get("default") is True
            or match_info.get("bye") is True
        ):
            if match_info.get("default") is True or (
                hasattr(envs[0], "default") and envs[0].default
            ):
                print(Fore.YELLOW + "Opponent Failed to Connect.")
                print(Fore.GREEN + f"Round {self.current_round} complete")
                print(Style.RESET_ALL)
                if self.current_round > self.maximum_rounds:
                    envs = None
                else:
                    envs, match_info = self.tournament.next_match()
                continue
            if match_info.get("bye") is True:
                print(Fore.GREEN + "Bye round")
                print(Fore.GREEN + f"Round {self.current_round} complete")
                print(Style.RESET_ALL)
                self.current_round += 1
                if self.current_round > self.maximum_rounds:
                    envs = None
                else:
                    envs, match_info = self.tournament.next_match()
                continue

            # run all episodes
            threads = []
            for env in envs:
                thread = threading.Thread(target=self.run_episode, args=(env, self.policy))
                thread.start()
                threads.append(thread)
                time.sleep(1)

            for thread in threads:
                thread.join()
            print(Fore.GREEN + f"Round {self.current_round} complete!")
            print(Style.RESET_ALL)
            self.current_round += 1

            if self.current_round > self.maximum_rounds:
                envs = None
            else:
                envs, match_info = self.tournament.next_match()

    @staticmethod
    def run_episode(env, policy):
        termination = False
        truncation = False
        timestep = 0
        reward = info = None
        initial_observation = env.reset()
        if initial_observation is None:
            # handling edge case of environment automatically resetting (e.g. opp instantly folds in Texas Holdem)
            termination = True
            observation = None
        else:
            observation, info = initial_observation
        while not (termination or truncation):
            with ThreadPool() as pool:
                try:
                    # self.num_turns += 1
                    action_surprise = pool.apply_async(policy, args=(
                        observation, reward, termination, truncation, info
                    )).get(timeout=TURN_LIMIT)
                except TimeoutError:
                    # self.num_default += 1
                    print(Fore.RED + "Time Limit Exceeded. Sending default action for environment.")
                    action_surprise = None
                except Exception as e:
                    print(Fore.RED + f"Error occurred while calling policy: {e}. "
                                     f"Sending default action for environment.")
            if action_surprise is None:
                # if error raised by policy or timed out
                if isinstance(observation, dict) and "action_mask" in observation.keys():
                    legal_mask = observation["action_mask"]
                    legal_actions = legal_mask.nonzero()[0]
                    action_surprise = np.random.choice(legal_actions)
                else:
                    action_surprise = "Pass"
            # Do some preemptive preprocessing of the user action
            if isinstance(action_surprise, tuple):
                action_surprise = (
                    validate_action(action_surprise[0]),
                    action_surprise[1],
                )
            else:
                action_surprise = validate_action(action_surprise)
            observation, reward, termination, truncation, info = env.step(
                action_surprise
            )  # Send action to game server
            # Print the action (response) if it is an LLM environment
            role = info.get("role")
            if role == "attacker":
                color = Fore.RED
            elif role == "defender":
                color = Fore.BLUE
            else:
                color = Fore.YELLOW
            if isinstance(action_surprise, str):
                print(color + f"[{role}]" + Fore.BLACK + f"{action_surprise}")
            elif isinstance(action_surprise, tuple) and isinstance(
                    action_surprise[0], str
            ):
                print(color + f"[{role}]" + Fore.BLACK + f"{action_surprise[0]}")
            timestep += 1