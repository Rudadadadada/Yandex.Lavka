import datetime

import pytest

URL_POST_COURIERS = 'couriers/'
URL_GET_COURIERS_META_INFO_COURIER_ID = 'couriers/meta-info/'
params = {'startDate': '2023-05-01', 'endDate': '2023-05-10'}

CORRECT_COURIERS = {'couriers': [{'courier_type': 'FOOT',
                                  'regions': [1],
                                  'working_hours': ['00:00-23:59']}]}


@pytest.mark.parametrize('courier_id, start_date, end_date',
                         [(1, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1)),
                          (500, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1)),
                          (1, datetime.date.today(), datetime.date.today())])
def test_get_courier_meta_info_ok(client, courier_id, start_date, end_date):
    client.post(URL_POST_COURIERS, json=CORRECT_COURIERS)
    response = client.get(URL_GET_COURIERS_META_INFO_COURIER_ID + '1', params={
        'courier_id': courier_id, 'start_date': start_date, 'end_date': end_date})
    assert response.status_code == 200

