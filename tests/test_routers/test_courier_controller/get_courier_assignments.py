import datetime

import pytest

URL_POST_COURIERS = 'couriers/'
URL_POST_ORDERS = 'orders/'
URL_POST_ORDERS_ASSIGN = 'orders/assign/'
URL_GET_COURIER_ASSIGNMENT = 'courier/assignments/'

CORRECT_COURIERS = [{'courier_type': 'FOOT',
                     'regions': [1],
                     'working_hours': ['00:00-23:59']}]

CORRECT_ORDERS = [{'weight': 1,
                   'region': 1,
                   'delivery_hours': ['00:00-23:59'],
                   'cost': 1}]


@pytest.mark.parametrize("date, courier_id", [(datetime.datetime.today().date(), 1)])
def test_get_courier_assignment_info_ok(client, date, courier_id):
    client.post(URL_POST_COURIERS, json=CORRECT_COURIERS)
    client.post(URL_POST_ORDERS, json=CORRECT_ORDERS)
    client.post(URL_POST_ORDERS_ASSIGN)
    response = client.get(URL_GET_COURIER_ASSIGNMENT, params={'date': date, 'courier_id': courier_id})
    assert response.status_code == 200
    response = client.get(URL_GET_COURIER_ASSIGNMENT, params={'date': date})
    assert response.status_code == 200


@pytest.mark.parametrize("date, courier_id", [(datetime.datetime.today().date(), 500)])
def test_get_courier_assignment_info_ok(client, date, courier_id):
    client.post(URL_POST_COURIERS, json=CORRECT_COURIERS)
    client.post(URL_POST_ORDERS, json=CORRECT_ORDERS)
    client.post(URL_POST_ORDERS_ASSIGN)
    response = client.get(URL_GET_COURIER_ASSIGNMENT, params={'date': date, 'courier_id': courier_id})
    assert response.status_code == 400
