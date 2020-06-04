from typing import Union, Dict

from lxml import html
import pytest


def extract_static_redirections_from_index_response(data: Union[bytes, str]) -> Dict[str, Dict[str, str]]:
    root = html.fromstring(data)

    rows = root.cssselect("#static-redirections > .row")

    static_redirections = {}

    for row in rows:
        target_col, short_names_col = (i[0] for i in row.cssselect(".column"))

        target_url = target_col.cssselect("a")[0].attrib["href"]
        short_names_anchors = short_names_col.cssselect("a")

        short_names = {a.cssselect("code")[0].text: a.attrib["href"] for a in short_names_anchors}

        static_redirections[target_url] = short_names

    return static_redirections


def test_index_empty_client(empty_client):
    response = empty_client.get("/")

    assert response.status_code == 200

    static_redirs = extract_static_redirections_from_index_response(b"".join(response.response))
    assert len(static_redirs) == 0


def test_index_with_data(test_data_client):
    response = test_data_client.get("/")

    assert response.status_code == 200

    static_redirs = extract_static_redirections_from_index_response(b"".join(response.response))
    assert len(static_redirs) == 1
    assert static_redirs["https://test.test"] == {"test1": "/test1"}


# FIXME: find out how to use fixtures for a parametrized test to get rid of ugly for loop
def test_shortener_nonexisting_name(empty_client, test_data_client, test_data_client_custom_cache,
                                    test_data_client_nocache):
    for client in [empty_client, test_data_client, test_data_client_custom_cache, test_data_client_nocache]:
        response = client.get("/qwertzuiop")

        assert response.status_code == 404


@pytest.mark.parametrize("name", ["test1", "test2", "test3"])
def test_shortener_existing_name_default_config(test_data_client, name):
    response = test_data_client.get("/{}".format(name))

    assert response.status_code == 301
    assert response.headers["cache-control"] == "max-age=120"
    assert response.headers["location"] == "https://test.test"


@pytest.mark.parametrize("name", ["test1", "test2", "test3"])
def test_shortener_existing_name_nocache(test_data_client_nocache, name):
    response = test_data_client_nocache.get("/{}".format(name))

    assert response.status_code == 302
    assert "cache_control" not in response.headers
    assert response.headers["location"] == "https://test.test"


@pytest.mark.parametrize("name", ["test1", "test2", "test3"])
def test_shortener_existing_name_custom_cache(test_data_client_custom_cache, name):
    response = test_data_client_custom_cache.get("/{}".format(name))

    assert response.status_code == 301
    assert response.headers["cache-control"] == "max-age={}".format(test_data_client_custom_cache._max_age)
    assert response.headers["location"] == "https://test.test"


@pytest.mark.parametrize("name", ["api", "api123", "api/", "api/123"])
def test_shortener_name_exceptions(test_data_client, name):
    response = test_data_client.get("/{}".format(name))

    assert response.status_code == 404
