URL = 'couriers/'

CORRECT_COURIERS = {'couriers': [{'courier_type': 'FOOT',
                                  'regions': [1],
                                  'working_hours': ['15:00-16:00']}]}


def test_rate_limiter_too_many_requests(client):
    for i in range(10):
        client.post(URL, json=CORRECT_COURIERS)
    response = client.post(URL, json=CORRECT_COURIERS)
    assert response.status_code == 429
