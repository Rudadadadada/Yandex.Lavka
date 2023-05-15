URL = 'couriers/'

CORRECT_COURIERS = {'couriers': [{'courier_type': 'FOOT',
                                  'regions': [1],
                                  'working_hours': ['15:00-16:00']}]}

INCORRECT_COURIERS = {'couriers': [{'courier_type': 'FOoT',
                                    'regions': [1],
                                    'working_hours': ['15:00-16:00']},
                                   {'courier_type': 'FOOT',
                                    'regions': [-1],
                                    'working_hours': ['15:00-16:00']},
                                   {'courier_type': 'FOOT',
                                    'regions': [1],
                                    'working_hours': ['15 : 00 - 24:60']}]}


def test_post_couriers_ok(client):
    response = client.post(URL, json=CORRECT_COURIERS)
    assert response.status_code == 200


def test_post_couriers_bad_request(client):
    response = client.post(URL, json=INCORRECT_COURIERS)
    assert response.status_code == 400
