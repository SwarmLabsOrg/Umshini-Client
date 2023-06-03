import argparse
import Umshini
from example_policy import DummyAgent

'''
    This is a simple example of connecting an agent to the umshini server.

    The agent is a simple policy function that chooses a random action.
    For more information on how to write a policy function, see example_policy.py

    This example script takes 3 command line arguments:
        1. The name of the environment to connect to
        2. The name of the bot
        3. The umshini account api key
'''

parser = argparse.ArgumentParser()
parser.add_argument("env_name", type=str, help="Name of environment for agent to compete in.")
parser.add_argument("bot_name", type=str, help="Name of bot to record results to.")
parser.add_argument("api_key", type=str, help="umshini API key.")

args = parser.parse_args()

agent = DummyAgent(args.env_name)
Umshini.connect(agent.env_name, args.bot_name, args.api_key, agent.pol)
