import numpy as np
import pytest

import umshini
from umshini import CLASSIC_GAMES, LLM_GAMES


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


@pytest.mark.parametrize("env_name", CLASSIC_GAMES)
def test_local_game_rl_kwargs(env_name):
    """Tests env-specific kwargs from PettingZoo environments."""
    if env_name == "connect_four_v3":
        umshini.local(
            env_name,
            rand_policy,
            rand_policy,
            max_steps=25,
            **dict(screen_scaling=9),
        )
    if env_name == "chess_v5":
        umshini.local(
            env_name,
            rand_policy,
            rand_policy,
            max_steps=25,
            **dict(screen_height=500),
        )
    if env_name == "go_v5":
        umshini.local(
            env_name,
            rand_policy,
            rand_policy,
            max_steps=25,
            **dict(screen_height=500, board_size=7, komi=7.5),
        )


@pytest.mark.parametrize("env_name", LLM_GAMES)
def test_local_game_llm_kwargs(env_name):
    """Tests env-specific kwargs from ChatArena environments."""
    umshini.local(
        env_name,
        rand_policy,
        rand_policy,
        **dict(
            round_length=2,
            string_observation=True,
            character_limit=8000,
            save_json=False,
            disable_judging=True,
        ),
    )
