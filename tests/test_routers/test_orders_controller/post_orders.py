URL = 'orders/'

CORRECT_ORDERS = {'orders': [{'weight': 1,
                              'region': 1,
                              'delivery_hours': ['15:00-16:00'],
                              'cost': 1}]}

INCORRECT_ORDERS = {'orders': [{'weight': 0,
                                'region': 1,
                                'delivery_hours': ['15:00-16:00'],
                                'cost': 1},
                               {'weight': 1,
                                'region': -1,
                                'delivery_hours': ['15:00-16:00'],
                                'cost': 1},
                               {'weight': 1,
                                'region': 1,
                                'delivery_hours': ['15 : 90  -  16----: 1560'],
                                'cost': 1},
                               {'weight': 1,
                                'region': 1,
                                'delivery_hours': ['15:00-16:00'],
                                'cost': -52352352}]}


def test_post_orders_ok(client):
    response = client.post(URL, json=CORRECT_ORDERS)
    assert response.status_code == 200


def test_post_orders_bad_request(client):
    response = client.post(URL, json=INCORRECT_ORDERS)
    assert response.status_code == 400
