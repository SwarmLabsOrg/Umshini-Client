import Umshini
import sys
import os
from envs.envs_list import make_test_env
from multiprocessing import Pool

'''
Spawns 8th and final player instance
'''

env = make_test_env("boxing_v1", seed = 1)
env.reset()
agent = env.agents[0]
action_space = env.action_spaces[agent]

def my_pol(obs, rew, done, info):
    return (action_space.sample(), 1) # use 1 for dummy surprise

Umshini.connect("boxing_v1", "user1", "test_user1", my_pol)