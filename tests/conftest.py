from pytest import fixture


def pytest_addoption(parser):
    parser.addoption("--env_name", action="store")


@fixture()
def env_name(request):
    return request.config.getoption("--env_name")
