import numpy as np
import pytest

import umshini
from umshini import ALL_ENVIRONMENTS


def rand_policy(obs, rew, term, trunc, info):
    """Return a random legal action."""
    # PettingZoo Classic RL environments
    if isinstance(obs, dict) and "action_mask" in obs.keys():
        legal_mask = obs["action_mask"]
        legal_actions = legal_mask.nonzero()[0]
        action = np.random.choice(legal_actions)
    # LLM environments
    else:
        action = "TEST_RESPONSE"
    return (action, 0)


def long_response_policy(obs, rew, term, trunc, info):
    response = "".join(map(str, range(1, 10000)))
    return (response, 0)


@pytest.mark.parametrize("env_name", ALL_ENVIRONMENTS)
def test_environment_verification(env_name):
    umshini.test(env_name)
