import pytest

URL = 'couriers/'


@pytest.mark.parametrize('limit, offset', [(1, 0), (1, 1), (2, 3), (50, 50), (7, 14)])
def test_get_couriers_ok(client, limit, offset):
    response = client.get(URL, params={'limit': limit, 'offset': offset})
    assert response.status_code == 200


@pytest.mark.parametrize('limit, offset', [(0, 0), (0, -1), (-1, -1), (-50, -10), (-50, 0)])
def test_get_couriers_bad_request(client, limit, offset):
    response = client.get(URL, params={'limit': limit, 'offset': offset})
    assert response.status_code == 400
