from supersuit import frame_skip_v0, frame_stack_v1
from pettingzoo.utils import aec_to_parallel, turn_based_aec_to_parallel


ATARI_GAMES = [
    "combat_tank_v2",
    "space_war_v2",
    "surround_v2"
]
CLASSIC_GAMES = [
    "connect_four_v3",
    "texas_holdem_no_limit_v6",
    "go_v5"
]
MAX_CYCLES = 10000


ALL_ENVIRONMENTS = ATARI_GAMES + CLASSIC_GAMES
all_environments = {}


class UnsupportedGameError(Exception):
    pass


def import_atari(env_name):
    try:
        from pettingzoo.atari import combat_tank_v2, space_war_v2, surround_v2
        all_environments["combat_tank_v2"] = combat_tank_v2
        all_environments["space_war_v2"] = space_war_v2
        all_environments["surround_v2"] = surround_v2
    except ImportError as err:
        print(f"You do not have the requested Atari game ({env_name}) installed.\n\
You can install it with `pip install umshini[atari]` and the AutoROM tool.")
        print(err, flush=True)
        raise err


def import_classic(env_name):
    try:
        from pettingzoo.classic import connect_four_v3, go_v5, texas_holdem_no_limit_v6
        all_environments["connect_four_v3"] = connect_four_v3
        all_environments["go_v5"] = go_v5
        all_environments["texas_holdem_no_limit_v6"] = texas_holdem_no_limit_v6
    except ImportError as err:
        print(f"You do not have the requested Classic game ({env_name}) installed.\n\
              You can install it with `pip install umshini[classic]`")
        print(err, flush=True)
        raise err


def make_test_env(game_id, seed=None, render_mode=None, turn_based=False):
    if game_id in ATARI_GAMES:
        import_atari(game_id)
        env = all_environments[game_id]
        env = env.env(render_mode=render_mode)
        env = frame_stack_v1(env, 4)
        env = frame_skip_v0(env, 4)
        env = aec_to_parallel(env)
        turn_based = False
    elif game_id in CLASSIC_GAMES:
        import_classic(game_id)
        env = all_environments[game_id]
        env = env.env(render_mode=render_mode)
        env = turn_based_aec_to_parallel(env)
        turn_based = True
    else:
        raise UnsupportedGameError

    # Check if game can be played with parallel API
    # turn_based = not test_env.metadata["is_parallelizable"]
    return env, turn_based
