import pytest

URL = 'couriers/'

CORRECT_COURIERS = {'couriers': [{'courier_type': 'FOOT',
                                  'regions': [1],
                                  'working_hours': ['15:00-16:00']}]}


def test_get_courier_ok(client):
    client.post(URL, json=CORRECT_COURIERS)
    response = client.get(URL + '1')
    assert response.status_code == 200


@pytest.mark.parametrize('courier_id', [0, -1])
def test_get_courier_bad_request(client, courier_id):
    response = client.get(URL + str(courier_id))
    assert response.status_code == 400


@pytest.mark.parametrize('courier_id', [100, 200, 300])
def test_get_courier_not_found(client, courier_id):
    response = client.get(URL + str(courier_id))
    assert response.status_code == 404
