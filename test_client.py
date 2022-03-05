import Umshini
from envs.envs_list import make_test_env
from multiprocessing import Pool

env = make_test_env("boxing_v1", seed = 1)
env.reset()
agent = env.agents[0]
action_space = env.action_spaces[agent]

def my_pol(obs, rew, done, info):
    return (action_space.sample(), 1) # use 1 for dummy surprise


#Umshini.connect("boxing_v1", "user1", "test_user1", my_pol)
user_nums =  [*range(1, 9)]
master_params = [("boxing_v1", "user" + str(i), "test_user" + str(i), my_pol) for i in user_nums]

with Pool(len(user_nums)) as pool:
    pool.starmap(Umshini.connect, master_params)