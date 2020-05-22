import json

import pytest

from redirector.non_database import NonDatabase


def check_empty_non_db(empty_non_db):
    assert empty_non_db.urls_to_names == {}
    assert empty_non_db.names_to_urls == {}


def test_construction_noargs():
    empty_non_db = NonDatabase()
    check_empty_non_db(empty_non_db)


def test_construction_empty_dict():
    empty_non_db = NonDatabase({})
    check_empty_non_db(empty_non_db)


def test_construction_non_existing_file():
    with pytest.raises(FileNotFoundError):
        NonDatabase("/i/do/not/exist")


def test_construction_existing_empty_file(tmpdir, monkeypatch):
    filename = "redirects.json"

    redirects = tmpdir.join(filename)

    # create file
    with open(redirects, "w"):
        pass

    with monkeypatch.context():
        monkeypatch.chdir(tmpdir)

        with pytest.raises(json.JSONDecodeError):
            NonDatabase(filename)


def test_construction_existing_broken_json_file(tmpdir, monkeypatch):
    filename = "redirects.json"

    redirects = tmpdir.join(filename)

    # create file
    with open(redirects, "w") as f:
        f.write("broken stuff")

    with monkeypatch.context():
        monkeypatch.chdir(tmpdir)

        with pytest.raises(json.JSONDecodeError):
            NonDatabase(filename)


def test_construction_empty_map_file(tmpdir, monkeypatch):
    filename = "redirects.json"

    redirects = tmpdir.join(filename)

    # create file
    with open(redirects, "w") as f:
        json.dump({}, f)

    with monkeypatch.context():
        monkeypatch.chdir(tmpdir)

        non_db = NonDatabase(filename)

    # we do this outside the above block, as after loading the data, the file should not be needed any more
    check_empty_non_db(non_db)


def test_deferred_loading_empty_data():
    non_db = NonDatabase()
    check_empty_non_db(non_db)

    non_db.load_data({})
    check_empty_non_db(non_db)


def test_construction_proper_data():
    data = {
        "https://bla.com": ["test"],
    }

    non_db = NonDatabase(data)

    assert non_db.urls_to_names == data

    reverse_map = {
        "test": "https://bla.com",
    }

    assert non_db.names_to_urls == reverse_map


def test_improper_name():
    data = {
        "https://bla.com": ["test/test"],
    }

    with pytest.raises(ValueError):
        NonDatabase(data)


def test_name_collision_name():
    data = {
        "https://bla.com": ["test"],
        "https://bla2.com": ["test"],
    }

    with pytest.raises(ValueError):
        NonDatabase(data)


def test_lookups():
    data = {
        "https://bla.com": ["bla", "bla1"],
        "https://bla2.com": ["bla2"],
    }

    non_db = NonDatabase(data)

    assert non_db.lookup_names_for_url("https://bla.com") == ["bla", "bla1"]
    assert non_db.lookup_names_for_url("https://bla2.com") == ["bla2"]

    assert non_db.lookup_url_for_name("bla") == "https://bla.com"
    assert non_db.lookup_url_for_name("bla1") == "https://bla.com"
    assert non_db.lookup_url_for_name("bla2") == "https://bla2.com"
