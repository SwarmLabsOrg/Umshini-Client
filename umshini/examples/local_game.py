import numpy as np

import umshini

def my_pol(obs, rew, term, trunc, info):
    legal_mask = obs["action_mask"]
    legal_actions = legal_mask.nonzero()[0]
    action = np.random.choice(legal_actions)
    return action

def opponent_pol(obs, rew, term, trunc, info):
    legal_mask = obs["action_mask"]
    legal_actions = legal_mask.nonzero()[0]
    action = np.random.choice(legal_actions)
    return action

umshini.local("connect_four_v3", my_pol, opponent_pol)
