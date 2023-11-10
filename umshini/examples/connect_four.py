import numpy as np

import umshini


def policy(observation, reward, termination, truncation, info):
    """Return a random legal action."""
    legal_mask = observation["action_mask"]
    legal_actions = legal_mask.nonzero()[0]
    action = np.random.choice(legal_actions)
    return (action, 0)


umshini.connect("connect_four_v3", "bot_user1_env1", "user1", policy)
