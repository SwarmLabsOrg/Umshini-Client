import sys
from colosseum.test_tournament_client import ColosseumTournamentAgent
from multiprocessing import Pool


def create_and_run(username):
    agent = ColosseumTournamentAgent(maximum_rounds=100)
    agent.connect(username, "password")
    agent.run()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python testTournamentClients.py user1 user2 ...")
        sys.exit()
    with Pool(len(sys.argv[1:])) as pool:
        pool.map(create_and_run, sys.argv[1:])
