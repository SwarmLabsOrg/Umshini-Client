import sys
from colosseum.test_tournament_client import ColosseumTournamentAgent
from multiprocessing import Pool

def create_and_run(username):
    agent = ColosseumTournamentAgent(maximum_rounds=100)
    agent.connect(username, "password")
    agent.run()


if __name__ == '__main__':
    print("Hello")
    with Pool(8) as pool:
        pool.map(create_and_run, sys.argv[1:])
    print("World")
