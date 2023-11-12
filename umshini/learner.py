# pyright: reportGeneralTypeIssues=false, reportOptionalCall=false
from __future__ import annotations

import inspect
import traceback

from colorama import Fore, Style
from halo import Halo

from umshini.envs import make_env
from umshini.example_client import UmshiniTournamentAgent
from umshini.examples.example_agent import DummyAgent


def create_and_run(botname, user_key):
    agent = UmshiniTournamentAgent(maximum_rounds=100)
    agent.connect(botname, user_key)
    agent.run()


def connect(environment, botname, user_key, user_policy, debug=False, testing=False):
    """User end function to add their RL policy.

    Policy function takes 5 arguments:
        observation: the observation of the environment
        reward: the reward of the last action
        termination: whether the episode is over
        truncation: whether the episode was truncated
        info: any additional information

    The policy function must return:
        action: the action to take
        surprise: the surprise value of the action [Optional]
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
    test(environment, user_policy)
    agent.connect(botname, user_key)
    agent.run()


def local(env_id: str, user_policy: callable, opponent_policy: callable):
    """User end function to run a local game for a given environment, using two provided policies.

    Each policy function takes 5 arguments:
        observation: the observation of the environment
        reward: the reward of the last action
        termination: whether the episode is over
        truncation: whether the episode was truncated
        info: any additional information

    The policy function must return:
        action: the action to take
        surprise: the surprise value of the action [Optional]
    """
    test(env_id, user_policy)
    test(env_id, opponent_policy)

    steps = 0
    winner = None
    score = None
    spinner = Halo(
        text=f"Playing local game: {env_id} (step: {steps})",
        text_color="cyan",
        color="green",
        spinner="dots",
    )
    spinner.start()

    env = make_env(env_id, render_mode="human", debug=False)
    env.reset()

    try:
        for agent in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()

            if termination or truncation:
                winner = max(env.rewards)
                score = env.rewards
                break

            else:
                if agent == env.possible_agents[0]:
                    action_surprise = user_policy(
                        observation, reward, termination, truncation, info
                    )
                else:
                    action_surprise = opponent_policy(
                        observation, reward, termination, truncation, info
                    )

                # Handle optional return without a surprise value
                if isinstance(action_surprise, tuple):
                    action = action_surprise[0]
                else:
                    action = action_surprise
            env.step(action)

            steps += 1
            spinner.text = f"Playing local game: {env_id} (step: {steps})"
        env.close()
        spinner.succeed()
        print(Fore.GREEN + f"Scores: {score}\nWinner: {winner}" + Style.RESET_ALL)

    except Exception:
        spinner.stop()
        print(
            Fore.RED
            + f"Local environment has raised an error (step: {steps})"
            + Style.RESET_ALL
        )
        print("\n" + Fore.RED + traceback.format_exc() + Style.RESET_ALL)
        quit()


def test(env_id: str, user_policy: callable | None = None):
    """User end function to test a policy on a given environment.

    The policy function takes 5 arguments:
        observation: the observation of the environment
        reward: the reward of the last action
        termination: whether the episode is over
        truncation: whether the episode was truncated
        info: any additional information

    The policy function must return:
        action: the action to take
        surprise: the surprise value of the action [Optional]
    """
    if user_policy is None:
        user_policy = DummyAgent(env_id).pol

    num_args = len(inspect.signature(user_policy).parameters)
    if num_args != 5:
        print(
            Fore.RED
            + f"Policy must take five input arguments: observation, reward, termination, truncation, info. Number of arguments: {num_args}"
            + Style.RESET_ALL
        )

    env = make_env(env_id, render_mode=None, debug=True)
    env.reset()

    try:
        for agent in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()

            if termination or truncation:
                action = None

            else:
                action_surprise = user_policy(
                    observation, reward, termination, truncation, info
                )

                # Handle optional return without a surprise value
                if isinstance(action_surprise, tuple):
                    action = action_surprise[0]
                else:
                    action = action_surprise
            env.step(action)
        env.close()
        print(
            Fore.GREEN
            + f"Policy has passed environment verification testing in {env_id} [{user_policy.__name__}]"
            + Style.RESET_ALL
        )

    except Exception:
        print(
            Fore.RED
            + f"Policy has failed verification testing in {env_id} [{user_policy.__name__}]"
        )
        print("\n" + Fore.RED + traceback.format_exc() + Style.RESET_ALL)
        quit()
