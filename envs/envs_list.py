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
from pettingzoo.classic import backgammon_v3
from pettingzoo.classic import checkers_v3
from pettingzoo.classic import chess_v5
from pettingzoo.classic import connect_four_v3
from pettingzoo.classic import gin_rummy_v4
from pettingzoo.classic import go_v5
from pettingzoo.classic import hanabi_v4
from pettingzoo.classic import leduc_holdem_v4
from pettingzoo.classic import rps_v2
from pettingzoo.classic import texas_holdem_v4
from pettingzoo.classic import texas_holdem_no_limit_v6
from pettingzoo.classic import tictactoe_v3
from pettingzoo.classic import uno_v4

from supersuit import frame_skip_v0, frame_stack_v1
from pettingzoo.utils import aec_to_parallel, turn_based_aec_to_parallel

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
    "backgammon_v3": backgammon_v3,
    "checkers_v3": checkers_v3,
    "chess_v5": chess_v5,
    "connect_four_v3": connect_four_v3,
    "gin_rummy_v4": gin_rummy_v4,
    "go_v5": go_v5,
    "hanabi_v4": hanabi_v4,
    "leduc_holdem_v4": leduc_holdem_v4,
    #"rps_v2": rps_v2,
    "texas_holdem_v4": texas_holdem_v4,
    "texas_holdem_no_limit_v6": texas_holdem_no_limit_v6,
    "tictactoe_v3": tictactoe_v3,
    "uno_v4": uno_v4,
}


def get_num_agents(name, env):
    count_env = env.env()
    count_env.reset()
    return count_env.num_agents


env_num_players = {name: get_num_agents(name, env) for name, env in all_environments.items()}

MAX_CYCLES = 10000


def make_test_env(game_id, seed):
    env = all_environments[game_id]
    # Check if game can be played with parallel API
    env_function = getattr(env, "parallel_env", None)
    if env_function and callable(env_function):
        print("Parallel")
        # TODO: Redo preprocessing by environment class
        env = env.env()
        env = frame_stack_v1(env, 4)
        env = frame_skip_v0(env, 4)
        env = aec_to_parallel(env)
        turn_based = False
    else:
        print("Turn Based")
        env = env.env()
        env = turn_based_aec_to_parallel(env)
        turn_based = True
    return env, turn_based
