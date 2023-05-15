import pytest

URL = 'orders/'

CORRECT_ORDERS = {'orders': [{'weight': 1,
                              'region': 1,
                              'delivery_hours': ['15:00-16:00'],
                              'cost': 1}]}


def test_get_order_ok(client):
    client.post(URL, json=CORRECT_ORDERS)
    response = client.get(URL + '1')
    assert response.status_code == 200


@pytest.mark.parametrize('order_id', [0, -1])
def test_get_order_bad_request(client, order_id):
    response = client.get(URL + str(order_id))
    assert response.status_code == 400


@pytest.mark.parametrize('order_id', [100, 200, 300])
def test_get_order_not_found(client, order_id):
    response = client.get(URL + str(order_id))
    assert response.status_code == 404
