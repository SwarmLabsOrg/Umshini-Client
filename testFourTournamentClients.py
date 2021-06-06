import sys
from colosseum.test_tournament_client import ColosseumTournamentAgent
from multiprocessing import Pool


def create_and_run(username):
    agent = ColosseumTournamentAgent()
    agent.connect(username, "password")
    agent.run()


if __name__ == '__main__':
    print("Hello")
    with Pool(5) as pool:
        pool.map(create_and_run, ["user1", "user2", "user3", "user4"])
    print("World")
