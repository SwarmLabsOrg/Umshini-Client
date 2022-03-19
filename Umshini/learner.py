import sys
from multiprocessing import Pool

from sqlalchemy import false
from .example_client import ColosseumTournamentAgent
from .tournament_client import TestEnv
from colorama import Fore, Style

def create_and_run(username, user_key):
    agent = ColosseumTournamentAgent(maximum_rounds=100)
    agent.connect(username, user_key)
    agent.run()

"""
User end function to add their RL policy

Passed function accepts parameters:
    policy(observation, reward, done, info)

Passed function returns action 
"""
def connect(environment, username, user_key, user_policy):
    agent = ColosseumTournamentAgent(policy=user_policy, games = [environment], maximum_rounds=100)
    agent.connect(username, user_key)
    agent.run()

def test(environment, user_policy):
    test_env = TestEnv(environment)
    done = False
    obs = rew = info = None
    for _ in range(100):
        try:
            (action, surprise) = user_policy(obs, rew, done, info)
            obs, rew, done, info = test_env.step(action)

            if done:
                print(Fore.GREEN + "Policy has passed verification testing in {}".format(environment))
                print(Style.RESET_ALL)
                break
        except:
            print(Fore.RED + "Policy has failed verification testing")
            print(Style.RESET_ALL)
            quit()
    
