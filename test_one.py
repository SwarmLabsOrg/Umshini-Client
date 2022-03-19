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

env = make_test_env("boxing_v1", seed = 1)
env.reset()
agent = env.agents[0]
action_space = env.action_spaces[agent]

def my_pol(obs, rew, done, info):
    return (action_space.sample(), 1) # use 1 for dummy surprise

Umshini.connect("boxing_v1", "user1", "test_user1", my_pol)

#Umshini.test("boxing_v1", my_pol)