def test_urls_empty_client(empty_client):
    response = empty_client.get("/api/urls.json")

    assert response.status_code == 200
    assert response.json == {}


def test_index_with_data(test_data_client, test_data):
    response = test_data_client.get("/api/urls.json")

    assert response.status_code == 200
    assert response.json == test_data
