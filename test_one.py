import Umshini
import numpy as np
from Umshini.envs.envs_list import make_test_env

'''
Spawns 8th and final player instance

Run this file (alone without the server) with the commented out Umshini.test line
in order to test local policy verification
'''
env_name = "connect_four_v3"
env, turn_based = make_test_env(env_name, seed=1)
env.reset()
agent = env.agents[0]
action_space = env.action_space(agent)


def my_pol(obs, rew, term, trunc, info):
    if (obs is not None and
        isinstance(obs, dict) and
        obs and
        "action_mask" in obs and
        any(obs["action_mask"] == 1)):
        action = np.random.choice(obs["action_mask"].nonzero()[0])
    else:
        action = env.action_space(env.agents[0]).sample()  # Choose a random action
    return (action, 1)   # use 1 for dummy surprise

Umshini.connect(env_name, "bot_user1_env2", "user1", my_pol)
