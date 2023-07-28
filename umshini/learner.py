# pyright: reportGeneralTypeIssues=false

from colorama import Fore, Style

from umshini.example_client import UmshiniTournamentAgent
from umshini.tournament_client import TestEnv


def create_and_run(botname, user_key):
    agent = UmshiniTournamentAgent(maximum_rounds=100)
    agent.connect(botname, user_key)
    agent.run()


def connect(environment, botname, user_key, user_policy, debug=False, testing=False):
    """User end function to add their RL policy.

    Passed function accepts parameters:
        policy(observation, reward, done, info)

    Passed function returns action
    """
    if testing:
        agent = UmshiniTournamentAgent(
            policy=user_policy,
            games=[environment],
            maximum_rounds=100,
            host="127.0.0.1",
            port="8803",
            debug=debug,
        )
    else:
        agent = UmshiniTournamentAgent(
            policy=user_policy,
            games=[environment],
            maximum_rounds=100,
            host="34.70.234.149",
            port="8803",
            debug=debug,
        )

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
                print(
                    Fore.GREEN
                    + f"Policy has passed verification testing in {environment}"
                )
                print(Style.RESET_ALL)
                break
        except:  # noqa: E722
            print(Fore.RED + "Policy has failed verification testing")
            print(Style.RESET_ALL)
            quit()
