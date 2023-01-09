import numpy as np
from Umshini.envs.envs_list import make_test_env

"""
    This is a simple example of a policy function that can be used to play
    in an Umshini environment.

    The policy function takes 5 arguments:
        obs: the observation of the environment
        rew: the reward of the last action
        term: whether the episode is over
        trunc: whether the episode was truncated
        info: any additional information

    The policy function must return a tuple of two elements:
        action: the action to take
        surprise: the surprise value of the action
"""


def pol(self, obs, rew, term, trunc, info):
    # If obs has an action mask, use that to select ana ction
    # Otherwise, sampel from the action space directly
    if (
        obs is not None
        and isinstance(obs, dict)
        and obs
        and "action_mask" in obs
        and any(obs["action_mask"] == 1)
    ):
        # Choose a random action
        action = np.random.choice(
            obs["action_mask"].nonzero()[0]
        )
    else:
        action = self.env.action_space(self.env.agents[0]).sample()
    return (action, 1)  # Return the action and a dummy surprise value of 1
