import numpy as np

from umshini.envs.envs_list import make_parallel_env

"""
    This is a simple example of a policy function that can be used to play
    in an Umshini environment.

    The policy function takes 5 arguments:
        observation: the observation of the environment
        reward: the reward of the last action
        termination: whether the episode is over
        truncation: whether the episode was truncated
        info: any additional information

    The policy function must return:
        action: the action to take
        surprise: the surprise value of the action [Optional]
"""


class DummyAgent:
    def __init__(self, env_name):
        self.env_name = env_name
        self.env, _ = make_parallel_env(env_name, seed=1)
        self.env.reset()

    def pol(self, obs, rew, term, trunc, info):
        if isinstance(obs, dict) and "action_mask" in obs:
            # If observation has an action mask, use that to select an action
            legal_mask = obs["action_mask"]
            legal_actions = legal_mask.nonzero()[0]
            action = np.random.choice(legal_actions)
        else:
            # Otherwise, sample from the action space directly
            action = self.env.action_space(self.env.agents[0]).sample()
        return (action, 1)
