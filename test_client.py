import Umshini
from envs.envs_list import make_test_env

def my_pol(obs, rew, done, info):
    env = make_test_env("boxing_v1", seed = 1)
    return (env.action_space.sample(), 1) # use 1 for dummy surprise

Umshini.connect("boxing_v1", "user1", "test_user1", my_pol)