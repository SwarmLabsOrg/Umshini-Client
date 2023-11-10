import numpy as np

import umshini


def my_pol(obs, rew, term, trunc, info):
    legal_mask = obs["action_mask"]
    legal_actions = legal_mask.nonzero()[0]
    action = np.random.choice(legal_actions)
    surprise = 1
    return action, surprise


def opponent_pol(obs, rew, term, trunc, info):
    legal_mask = obs["action_mask"]
    legal_actions = legal_mask.nonzero()[0]
    action = np.random.choice(legal_actions)
    surprise = 0
    return action, surprise


umshini.local("go_v5", my_pol, opponent_pol)