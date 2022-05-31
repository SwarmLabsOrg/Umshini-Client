import sys
import os
import numpy as np
from multiprocessing import Pool
import Umshini
from envs.envs_list import make_test_env

'''
Test Script, does what the old system test script does and spawns 7 players in a processing pool
WITHOUT output

Use test_one.py to spawn last client w text output

Hardcoded for 7 players user2 - user8 (the 7 players the DB spin up script creates)

I wrote this so we can continue to use this client repo to test, before release we should delete this
file from the client repo and have actual unit tests instead
'''
env_name = "boxing_v2"
env, turn_based = make_test_env(env_name, seed=1)
env.reset()
agent = env.agents[0]
action_space = env.action_spaces[agent]


def my_pol(obs, rew, done, info):
    if (obs is not None and
        isinstance(obs, dict) and
        obs and
        "action_mask" in obs and
        any(obs["action_mask"] == 1)):
        action = np.random.choice(obs["action_mask"].nonzero()[0])
    else:
        action = env.action_space(env.agents[0]).sample()  # Choose a random action
    return (action, 1)   # use 1 for dummy surprise


def mute():
    sys.stdout = open(os.devnull, 'w')

# Change _env to correct ID matching testing env 
user_nums =  [*range(2, 5)]
master_params = [(env_name, "bot_user{}_env{}".format(i, 1), "test_user" + str(i), my_pol) for i in user_nums]

if __name__ == "__main__":
    with Pool(len(user_nums), initializer=mute) as pool:
        pool.starmap(Umshini.connect, master_params)
