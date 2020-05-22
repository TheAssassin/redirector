import json

import pytest
from flask import Flask

from redirector.non_database import FlaskNonDatabase, NonDatabase


def test_default_initialization():
    ext = FlaskNonDatabase()

    with pytest.raises(RuntimeError):
        # try to access property
        ext.non_db()


def test_empty_file_default_filename_nonexisting_file(tmpdir, monkeypatch):
    with monkeypatch.context():
        monkeypatch.chdir(tmpdir)

        with pytest.warns(UserWarning, match="no redirections database path specified and redirects.json not found"):
            app = Flask(__name__)

            ext = FlaskNonDatabase(app)
            assert isinstance(ext.non_db, NonDatabase)


def test_empty_file_default_filename_empty_map(tmpdir, monkeypatch):
    with monkeypatch.context():
        monkeypatch.chdir(tmpdir)

        with open(tmpdir.join("redirects.json"), "w") as f:
            json.dump({}, f)

        app = Flask(__name__)

        ext = FlaskNonDatabase(app)
        assert isinstance(ext.non_db, NonDatabase)


def test_empty_file_custom_filename_nonexisting_file(tmpdir, monkeypatch):
    # use a tempdir to ensure the file does not exist
    with monkeypatch.context():
        monkeypatch.chdir(tmpdir)

        app = Flask(__name__)
        app.config["REDIRECTIONS_MAP_PATH"] = str(tmpdir.join("test.json"))

        with pytest.raises(FileNotFoundError):
            FlaskNonDatabase(app)


def test_empty_file_custom_filename_empty_map_file(tmpdir, monkeypatch):
    with monkeypatch.context():
        # create a file in the tmpdir but do _not_ chdir there
        tmpfile = tmpdir.join("test.json")

        with open(tmpfile, "w") as f:
            json.dump({}, f)

        app = Flask(__name__)
        app.config["REDIRECTIONS_MAP_PATH"] = str(tmpfile)

        ext = FlaskNonDatabase(app)
        assert isinstance(ext.non_db, NonDatabase)
