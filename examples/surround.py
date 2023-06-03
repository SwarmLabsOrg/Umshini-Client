import umshini
from umshini.envs.envs_list import make_test_env


try:
    sample_env, _ = make_test_env("surround_v2")
    sample_env.reset()
except ImportError:
    quit()


def policy(obs, rew, term, trunc, info):
    """
    Return a random legal action
    """
    action = sample_env.action_space(sample_env.agents[0]).sample()
    return (action, 0)


umshini.connect("surround_v2", "bot_user1_env1", "user1", policy)
