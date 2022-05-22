import Umshini
import sys
import os
from envs.envs_list import make_test_env
from multiprocessing import Pool

'''
Test Script, does what the old system test script does and spawns 7 players in a processing pool
WITHOUT output

Use test_one.py to spawn last client w text output

Hardcoded for 7 players user2 - user8 (the 7 players the DB spin up script creates)

I wrote this so we can continue to use this client repo to test, before release we should delete this
file from the client repo and have actual unit tests instead
'''

env = make_test_env("boxing_v2", seed = 1)
env.reset()
agent = env.agents[0]
action_space = env.action_spaces[agent]

def my_pol(obs, rew, done, info):
    return (action_space.sample(), 1) # use 1 for dummy surprise

def mute():
    sys.stdout = open(os.devnull, 'w')

# Umshini.connect("boxing_v1", "user1", "test_user1", my_pol)
# Change _env to correct ID matching testing env 
user_nums =  [*range(2, 5)]
master_params = [("boxing_v2", "bot_user{}_env{}".format(i, 1), "test_user" + str(i), my_pol) for i in user_nums]

if __name__ == "__main__":
    with Pool(len(user_nums), initializer=mute) as pool:
        pool.starmap(Umshini.connect, master_params)

#Umshini.connect("boxing_v1", "user1", "test_user1", my_pol)
