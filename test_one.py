import Umshini
import sys
import os
from envs.envs_list import make_test_env
from multiprocessing import Pool

'''
Spawns 8th and final player instance

Run this file (alone without the server) with the commented out Umshini.test line
in order to test local policy verification 
'''

env = make_test_env("boxing_v2", seed = 1)
env.reset()
agent = env.agents[0]
action_space = env.action_space(agent)

def my_pol(obs, rew, done, info):
    return (action_space.sample(), 1) # use 1 for dummy surprise

Umshini.connect("boxing_v2", "bot_user{}_env{}".format(1, 1), "test_user1", my_pol)

Umshini.test("boxing_v2", my_pol)
