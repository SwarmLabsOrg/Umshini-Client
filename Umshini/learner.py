import sys
from multiprocessing import Pool
from .example_client import ColosseumTournamentAgent


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

