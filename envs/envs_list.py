from pettingzoo.atari import boxing_v1
from pettingzoo.atari import combat_tank_v1
from pettingzoo.atari import combat_plane_v1
from pettingzoo.atari import double_dunk_v2
from pettingzoo.atari import entombed_competitive_v2
from pettingzoo.atari import entombed_cooperative_v2
from pettingzoo.atari import flag_capture_v1
from pettingzoo.atari import joust_v2
from pettingzoo.atari import ice_hockey_v1
from pettingzoo.atari import maze_craze_v2
from pettingzoo.atari import mario_bros_v2
from pettingzoo.atari import othello_v2
from pettingzoo.atari import basketball_pong_v2
from pettingzoo.atari import pong_v2
from pettingzoo.atari import foozpong_v2
from pettingzoo.atari import quadrapong_v3
from pettingzoo.atari import volleyball_pong_v2
from pettingzoo.atari import space_invaders_v1
from pettingzoo.atari import space_war_v1
from pettingzoo.atari import surround_v1
from pettingzoo.atari import tennis_v2
from pettingzoo.atari import video_checkers_v3
from pettingzoo.atari import wizard_of_wor_v2
from pettingzoo.atari import warlords_v2
from pettingzoo.classic import connect_four_v3

from supersuit import frame_skip_v0, frame_stack_v1

all_environments = {
    "boxing_v1": boxing_v1,
    "combat_tank_v1": combat_tank_v1,
    "combat_plane_v1": combat_plane_v1,
    "double_dunk_v2": double_dunk_v2,
    "entombed_cooperative_v2": entombed_cooperative_v2,
    "entombed_competitive_v2": entombed_competitive_v2,
    "flag_capture_v1": flag_capture_v1,
    "joust_v2": joust_v2,
    "ice_hockey_v1": ice_hockey_v1,
    "maze_craze_v2": maze_craze_v2,
    "mario_bros_v2": mario_bros_v2,
    "othello_v2": othello_v2,
    "pong_v2": pong_v2,
    "basketball_pong_v2": basketball_pong_v2,
    "foozpong_v2": foozpong_v2,
    "quadrapong_v3": quadrapong_v3,
    "volleyball_pong_v2": volleyball_pong_v2,
    "space_invaders_v1": space_invaders_v1,
    "space_war_v1": space_war_v1,
    "surround_v1": surround_v1,
    "tennis_v2": tennis_v2,
    "video_checkers_v3": video_checkers_v3,
    "wizard_of_wor_v2": wizard_of_wor_v2,
    "warlords_v2": warlords_v2,
    "connect_four_v3": connect_four_v3,
}


def get_num_agents(env):
    count_env = env.env()
    count_env.reset()
    return count_env.num_agents


env_num_players = {name: get_num_agents(env) for name, env in all_environments.items()}

MAX_CYCLES = 10000


def make_test_env(game_id, seed, turn_based=False):
    env = all_environments[game_id]
    # Check if game can be played with parallel API
    env_function = getattr(env, "parallel_env", None)
    if not turn_based and env_function and callable(env_function):
        print("Parallel")
        env = env.parallel_env(seed=seed, max_cycles=MAX_CYCLES)
        # TODO: Redo preprocessing by environment class
        env = frame_stack_v1(env, 4)
        env = frame_skip_v0(env, 4)
    else:
        print("Turn-based")
        env = env.env()
    return env
