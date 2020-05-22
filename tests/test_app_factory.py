import json

import pytest
from flask import Flask

from redirector import create_app, non_db_ext


def check_app_in_general(app: Flask):
    assert app.name == "redirector"

    # check that extension is initialized
    assert non_db_ext.non_db is not None


@pytest.fixture
def app(tmpdir, monkeypatch):
    with monkeypatch.context():
        monkeypatch.chdir(str(tmpdir))

        with pytest.warns(UserWarning, match="no redirections database path specified and redirects.json not found"):
            app = create_app()

    return app


def test_create_app_without_redirections_file(app):
    # make sure we're in a tempdir so that we can guarantee that redirections.json does not exist
    check_app_in_general(app)


def test_create_app_with_custom_max_age_from_environment(monkeypatch):
    env_var_name = "STATIC_REDIRECTIONS_MAX_AGE"
    env_var_value = "1234"

    with monkeypatch.context():
        monkeypatch.setenv(env_var_name, env_var_value)

        app = create_app()

    assert app.config[env_var_name] == env_var_value


def test_create_app_with_custom_redirections_file_path_from_environment(tmpdir, monkeypatch):
    # create temporary file with empty map to avoid raising exceptions
    tmpfile = tmpdir.join("redirects.json")

    with open(tmpfile, "w") as f:
        json.dump({}, f)

    env_var_name = "REDIRECTIONS_MAP_PATH"
    env_var_value = str(tmpfile)

    with monkeypatch.context():

        monkeypatch.setenv(env_var_name, env_var_value)

        app = create_app()

    assert app.config[env_var_name] == env_var_value
