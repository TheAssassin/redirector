import json

import pytest

import redirector


def make_client(tmpdir, static_routes: dict = None, config: dict = None):
    """
    Sets up an example app using the data passed as an argument and creates a test client to simulate requests.

    :param static_routes: static routes map following the common data format
    :param config: optional configuration to pass to the app
    :return: yields an app and test client
    """

    if config is None:
        config = {}

    # the only way to pass static routes to the app is to provide a routes file at the moment
    # therefore, if static routes have been
    if static_routes is not None:
        tmpfile = tmpdir.join("redirects.json")

        with open(tmpfile, "w") as f:
            json.dump(static_routes, f)

        config["REDIRECTIONS_MAP_PATH"] = str(tmpfile)

    app = redirector.create_app(config)

    test_client = app.test_client()

    return app, test_client


@pytest.fixture
def empty_client(tmpdir, monkeypatch):
    # make sure we're in a tempdir so that we can guarantee that redirections.json does not exist
    with monkeypatch.context():
        monkeypatch.chdir(str(tmpdir))

        with pytest.warns(UserWarning, match="no redirections database path specified and redirects.json not found"):
            _, test_client = make_client(tmpdir)
            yield test_client


@pytest.fixture
def test_data():
    return {
        "https://test.test": ["test1", "test2", "test3"]
    }


@pytest.fixture
def test_data_client(tmpdir, test_data):
    _, test_client = make_client(tmpdir, test_data)
    return test_client


@pytest.fixture(params=[1, 10, 100, 1000, 10000])
def test_data_client_custom_cache(tmpdir, test_data, request):
    max_age = request.param

    config = {
        "STATIC_REDIRECTIONS_MAX_AGE": max_age
    }

    _, test_client = make_client(tmpdir, test_data, config=config)

    # dirty hack to allow timeout to be read by users of the fixture
    test_client._max_age = max_age

    return test_client


@pytest.fixture(params=[0, -1, -100, -1000, -10000])
def test_data_client_nocache(tmpdir, test_data, request):
    max_age = request.param

    config = {
        "STATIC_REDIRECTIONS_MAX_AGE": max_age
    }

    _, test_client = make_client(tmpdir, test_data, config=config)
    return test_client
