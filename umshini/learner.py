# pyright: reportGeneralTypeIssues=false, reportOptionalCall=false
from __future__ import annotations

import inspect
import time
import traceback

from colorama import Fore, Style
from halo import Halo

from umshini.envs import LLM_GAMES, make_env
from umshini.example_client import UmshiniTournamentAgent
from umshini.examples.example_agent import DummyAgent


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


def local(
    env_id: str,
    user_policy: callable,
    opponent_policy: callable,
    max_steps: int | None = None,
    **kwargs,
):
    """User end function to run a local game for a given environment, using two provided policies.

    Use kwargs to specify environment specific keyword arguments.
    For RL environments, see https://pettingzoo.farama.org/environments/classic/
    For LLM environments, see https://github.com/Farama-Foundation/chatarena/blob/main/chatarena/environments/umshini/pettingzoo_wrapper.py#L45

    Note: "render_mode" kwarg cannot be specified as a kwarg, as rendering is always enabled for local testing.

    Example:
        >>> import umshini
        >>> def test_policy(observation, reward, termination, truncation, info):
        ...     return ("TEST RESPONSE", 0)
        ...
        >>> umshini.local("deception", test_policy, test_policy, **dict(round_length=2, string_observation=True, character_limit=8000, save_json=False, disable_judging=True))

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
    if env_id in LLM_GAMES:
        time.sleep(0.2)  # Ensures printing works with spinner

    env = make_env(env_id, render_mode="human", debug=False, **kwargs)
    env.reset()

    try:
        for agent in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()

            if (termination or truncation) or (
                max_steps is not None and steps >= max_steps
            ):
                winner = (
                    max(env.rewards)
                    if not all(value == 0 for value in env.rewards.values())
                    else None
                )
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
            steps += 1
            spinner.text = f"Playing local game: {env_id} (step: {steps})"
            if env_id in LLM_GAMES:
                time.sleep(0.2)  # Ensures printing works with spinner
            env.step(action)
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

    if env_id in LLM_GAMES:
        env = make_env(env_id, render_mode=None, debug=True, round_length=2)
    else:
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
