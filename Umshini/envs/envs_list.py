from pettingzoo.atari import (boxing_v2,
                              combat_tank_v2,
                              combat_plane_v2,
                              double_dunk_v3,
                              entombed_competitive_v3,
                              entombed_cooperative_v3,
                              flag_capture_v2,
                              joust_v3,
                              ice_hockey_v2,
                              mario_bros_v3,
                              othello_v3,
                              basketball_pong_v3,
                              pong_v3,
                              foozpong_v3,
                              quadrapong_v4,
                              volleyball_pong_v3,
                              space_invaders_v2,
                              space_war_v2,
                              surround_v2,
                              tennis_v3,
                              video_checkers_v4,
                              wizard_of_wor_v3,
                              warlords_v3)
from pettingzoo.classic import (chess_v5,
                                connect_four_v3,
                                gin_rummy_v4,
                                go_v5,
                                hanabi_v4,
                                leduc_holdem_v4,
                                rps_v2,
                                texas_holdem_v4,
                                texas_holdem_no_limit_v6,
                                tictactoe_v3)

from supersuit import frame_skip_v0, frame_stack_v1
from pettingzoo.utils import aec_to_parallel, turn_based_aec_to_parallel

all_environments = {
    "boxing_v2": boxing_v2,
    "combat_tank_v2": combat_tank_v2,
    "combat_plane_v2": combat_plane_v2,
    "double_dunk_v3": double_dunk_v3,
    "entombed_cooperative_v3": entombed_cooperative_v3,
    "entombed_competitive_v3": entombed_competitive_v3,
    "flag_capture_v2": flag_capture_v2,
    "joust_v3": joust_v3,
    "ice_hockey_v2": ice_hockey_v2,
    "mario_bros_v3": mario_bros_v3,
    "othello_v3": othello_v3,
    "pong_v3": pong_v3,
    "basketball_pong_v3": basketball_pong_v3,
    "foozpong_v3": foozpong_v3,
    "quadrapong_v4": quadrapong_v4,
    "volleyball_pong_v3": volleyball_pong_v3,
    "space_invaders_v2": space_invaders_v2,
    "space_war_v2": space_war_v2,
    "surround_v2": surround_v2,
    "tennis_v3": tennis_v3,
    "video_checkers_v4": video_checkers_v4,
    "wizard_of_wor_v3": wizard_of_wor_v3,
    "warlords_v3": warlords_v3,
    "connect_four_v3": connect_four_v3,
    "gin_rummy_v4": gin_rummy_v4,
    "go_v5": go_v5,
    "hanabi_v4": hanabi_v4,
    "leduc_holdem_v4": leduc_holdem_v4,
    #"rps_v2": rps_v2,
    "texas_holdem_v4": texas_holdem_v4,
    "texas_holdem_no_limit_v6": texas_holdem_no_limit_v6,
    "tictactoe_v3": tictactoe_v3,
}


def get_num_agents(name, env):
    count_env = env.env()
    count_env.reset()
    return count_env.num_agents


env_num_players = {name: get_num_agents(name, env) for name, env in all_environments.items()}

MAX_CYCLES = 10000


def make_test_env(game_id, seed=None, render_mode=None, turn_based=False):
    env = all_environments[game_id]
    # Check if game can be played with parallel API
    test_env = env.env()
    turn_based = not test_env.metadata["is_parallelizable"]
    if turn_based:
        env = env.env(render_mode=render_mode)
        env = turn_based_aec_to_parallel(env)
    else:
        # TODO: Redo preprocessing by environment class
        env = env.env(render_mode=render_mode)
        env = frame_stack_v1(env, 4)
        env = frame_skip_v0(env, 4)
        env = aec_to_parallel(env)
    return env, turn_based
