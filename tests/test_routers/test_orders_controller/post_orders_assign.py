URL_POST_COURIERS = 'couriers/'
URL_POST_ORDERS = 'orders/'
URL_POST_ORDERS_ASSIGN = 'orders/assign/'

CORRECT_COURIERS = [[{'courier_type': 'FOOT',
                      'regions': [1],
                      'working_hours': ['00:00-23:59']}]]

CORRECT_ORDERS = {'orders': [{'weight': 1,
                              'region': 1,
                              'delivery_hours': ['15:00-16:00'],
                              'cost': 1},
                             {'weight': 1,
                              'region': 1,
                              'delivery_hours': ['15:00-16:00'],
                              'cost': 1},
                             {'weight': 1,
                              'region': 1,
                              'delivery_hours': ['15:00-16:00'],
                              'cost': 1}
                             ]}


def test_post_couriers_ok(client):
    client.post(URL_POST_COURIERS, json=CORRECT_COURIERS)
    client.post(URL_POST_ORDERS, json=CORRECT_ORDERS)
    response = client.post(URL_POST_ORDERS_ASSIGN)
    assert response.status_code == 201
