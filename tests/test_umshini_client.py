from multiprocessing import Pool
from typing import Callable

import numpy as np

import umshini


def rand_policy(obs, rew, term, trunc, info):
    """Return a random legal action."""
    if isinstance(obs, dict) and "action_mask" in obs.keys():
        legal_mask = obs["action_mask"]
        legal_actions = legal_mask.nonzero()[0]
        action = np.random.choice(legal_actions)
    else:
        action = "TEST_RESPONSE"
    return (action, 0)


def run_player(
    env_name: str, botname: str, userkey: str, policy: Callable, testing: bool
):
    umshini.connect(
        env_name,
        botname,
        userkey,
        policy,
        debug=testing,
        testing=testing,
    )


def test_umshini_client(
    env_name: str = "connect_four_v3", num_players: int = 4, testing: bool = True
):
    assert isinstance(num_players, int)
    assert isinstance(testing, bool)
    if num_players is None:
        num_players = 4
    env_to_id = {
        "go_v5": 1,
        "connect_four_v3": 2,
        "texas_holdem_no_limit_v6": 3,
        "debate": 4,
        "content_moderation": 5,
        "deception": 6,
    }
    env_id = env_to_id[env_name]
    args = []
    for i in range(1, 1 + num_players):
        args.append((env_name, f"user{i}_{env_id}", f"user{i}", rand_policy, testing))

    with Pool(num_players) as pool:
        pool.starmap(run_player, args)

    print("Test Passed")
