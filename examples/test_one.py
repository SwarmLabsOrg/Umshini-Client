import sys
import Umshini
from example_policy import DummyAgent

'''
    This is a simple example of connecting an agent to the Umshini server.

    The agent is a simple policy function that chooses a random action.
    For more information on how to write a policy function, see example_policy.py

    This example script takes 3 command line arguments:
        1. The name of the environment to connect to
        2. The name of the bot
        3. The Umshini account api key
'''

agent = DummyAgent(sys.argv[1])
Umshini.connect(agent.env_name, sys.argv[2], sys.argv[3], agent.pol)
