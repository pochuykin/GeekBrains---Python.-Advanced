import pytest
from datetime import datetime
from echo.controllers import get_echo


@pytest.fixture
def action_fixture():
    print('connect to db')
    return 'echo'


@pytest.fixture
def time_fixture():
    return datetime.now().timestamp()


@pytest.fixture
def data_fixture():
    return 'some data'


@pytest.fixture
def response_fixture(action_fixture, time_fixture, data_fixture):
    return {
        'action': action_fixture,
        'time': time_fixture,
        'data': data_fixture,
        'user': None,
        'code': 200
    }


@pytest.fixture
def request_fixture(action_fixture, time_fixture, data_fixture):
    return {
        'action': action_fixture,
        'time': time_fixture,
        'data': data_fixture
    }


def test_get_echo(request_fixture, response_fixture):
    response = get_echo(request_fixture)

    assert response_fixture.get('code') == response.get('code')
    # assert expected == request


def test_wrong_get_echo():
    action_mode = 'echo'
    data = 'some data'