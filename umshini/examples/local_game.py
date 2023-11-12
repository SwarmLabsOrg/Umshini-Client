import numpy as np

import umshini


def my_pol(obs, rew, term, trunc, info):
    if "action_mask" in obs:
        legal_mask = obs["action_mask"]
        legal_actions = legal_mask.nonzero()[0]
        action = np.random.choice(legal_actions)
    else:
        action = "I am the winner."
    return action


def opponent_pol(obs, rew, term, trunc, info):
    if "action_mask" in obs:
        legal_mask = obs["action_mask"]
        legal_actions = legal_mask.nonzero()[0]
        action = np.random.choice(legal_actions)
    else:
        action = "He is lying, I am the winner."
    return action


umshini.local("go_v5", my_pol, opponent_pol)
umshini.local("connect_four_v3", my_pol, opponent_pol)
umshini.local("texas_holdem_no_limit_v6", my_pol, opponent_pol)
umshini.local("debate", my_pol, opponent_pol)
umshini.local("content_moderation", my_pol, opponent_pol)
umshini.local("deception", my_pol, opponent_pol)
