from .example_client import ColosseumTournamentAgent
from .tournament_client import TestEnv
from colorama import Fore, Style


def create_and_run(botname, user_key):
    agent = ColosseumTournamentAgent(maximum_rounds=100)
    agent.connect(botname, user_key)
    agent.run()


def connect(environment, botname, user_key, user_policy, debug=False):
    """
    User end function to add their RL policy

    Passed function accepts parameters:
        policy(observation, reward, done, info)

    Passed function returns action
    """
    agent = ColosseumTournamentAgent(policy=user_policy, games=[environment], maximum_rounds=100, host="34.70.234.149",
                                     port="8803", debug=debug)
    #agent = ColosseumTournamentAgent(policy=user_policy, games=[environment],
    #                                 maximum_rounds=100, debug=debug)
    agent.connect(botname, user_key)
    agent.run()


def test(environment, user_policy):
    test_env = TestEnv(environment)
    term = trunc = False
    obs = rew = info = None
    for _ in range(100):
        try:
            (action, surprise) = user_policy(obs, rew, term, trunc, info)
            obs, rew, term, trunc, info = test_env.step(action)

            if term or trunc:
                print(Fore.GREEN + "Policy has passed verification testing in {}".format(environment))
                print(Style.RESET_ALL)
                break
        except:
            print(Fore.RED + "Policy has failed verification testing")
            print(Style.RESET_ALL)
            quit()
