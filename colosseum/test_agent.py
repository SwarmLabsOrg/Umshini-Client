import sys
import argparse
import time
from utils.socket_wrap import SocketWrapper
from .game_client import MatchmakerConnection
from .game_client import NetworkEnv
from envs.envs_list import all_environments

# Create command line argument parser
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
parser.add_argument(
    "-d", "--direct", action="store_true", help="Connect directly to game server"
)
parser.add_argument(
    "-g",
    "--games",
    type=str,
    choices=[list(all_environments.keys())],
    nargs=argparse.REMAINDER,
    help="Games you want to play",
)

# Set default command line arguments
parser.set_defaults(
    host="localhost", port=12345, games=["__all__"], latency=0, direct=False
)

# Parse arguments from the command line
args = parser.parse_args()

# Create matchmaking server connection, or direct game server connection
env = None
if args.direct:
    env = NetworkEnv(
        "boxing_v1", 5545551, "localhost", 35011, args.username, "A4C1B65BCE1D6EA4"
    )
else:
    mm_env = MatchmakerConnection(
        args.host, args.port, args.username, args.password, available_games=args.games
    )
    env = mm_env.start_new()

for i in range(100000):
    if i % 100 == 0:
        print("Timestep {}".format(i))
    time.sleep(args.latency / 1000)  # Used to simulate network latency
    action = env.action_space.sample()  # Choose a random action
    obs, rew, done, info = env.step(action)  # Send action to game server
    if done:
        print("Done")
        break  # Episode ended

#    conenv.render()
