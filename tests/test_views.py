import pytest


def test_index_empty_client(empty_client):
    response = empty_client.get("/")

    assert response.status_code == 200
    assert b"".join(response.response) == b""


def test_index_with_data(test_data_client):
    response = test_data_client.get("/")

    assert response.status_code == 200
    assert b"".join(response.response) == b"https://test.test: ['test1', 'test2', 'test3']"


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
