import sys
import argparse
import time
from colosseum.utils.socket_wrap import SocketWrapper
from colosseum.game_client import LeaderboardConnection
from colosseum.game_client import SingConnectEnv
from colosseum.envs.envs_list import all_environments

parser = argparse.ArgumentParser(description="Process options.")
parser.add_argument("username", type=str, help="Name of agent")
parser.add_argument("password", type=str, help="Password for agent")
parser.add_argument(
    "-i", "--host", type=str, help="Host ip of matchmaking or game server"
)
parser.add_argument(
    "-p", "--port", type=int, help="Host port of matchmaking or game server"
)
parser.add_argument(
    "-l", "--latency", type=int, help="Simulate network latency when sending actions"
)

# TODO: Potentially change this to games. Ask about th eproper interface for this
parser.add_argument(
    "-g",
    "--games",
    type=str,
    choices=[list(all_environments.keys())],
    nargs=argparse.REMAINDER,
    help="Games you want to play",
)
parser.set_defaults(host="localhost", port=12345, games=["__all__"], latency=0)

args = parser.parse_args()
# print(args)

leader_env = LeaderboardConnection(
    args.host, args.port, args.username, args.password, available_games=args.games
)

env = leader_env.start_new()
# env = SingConnectEnv(
#    "boxing_v0", 5545551, "localhost", 35011, args.username, "A4C1B65BCE1D6EA4"
# )
print("reset")
env.reset()
for i in range(100000):
    print("stepped")
    time.sleep(args.latency/1000)
    obs, rew, done, info = env.step(env.action_space.sample())
    if done:
        print("finished!")
        break

#    conenv.render()
