import datetime
from typing import Set

from app.database.__models import Courier, Region, CourierRegion, CourierWorkingHour
from app.database.db_session import create_session
from app.schemas.__schemes import CouriersModel


async def post_couriers(couriers: CouriersModel):
    session = create_session()

    for courier in couriers.couriers:
        new_courier = Courier(courier_type=courier.courier_type)
        session.add(new_courier)
        session.commit()

        for region in courier.regions:
            new_region = Region(region=region)
            session.add(new_region)
            session.commit()

            new_courier_region = CourierRegion(courier_id=new_courier.id, region_id=new_region.id)
            session.add(new_courier_region)
            session.commit()

        for cur_wh in courier.working_hours:
            separated_wh = cur_wh.split('-')
            start_time = separated_wh[0]
            end_time = separated_wh[1]

            new_wh = CourierWorkingHour(courier_id=new_courier.id, start_time=start_time, end_time=end_time)
            session.add(new_wh)
            session.commit()


async def get_courier_by_id(courier_id: int):
    def time_to_string(time) -> str:
        start_time = str(time[0].hour) + ':' + str(time[0].minute)
        end_time = str(time[1].hour) + ':' + str(time[1].minute)
        return start_time + '-' + end_time

    session = create_session()

    courier_info = {}

    type = session.query(Courier.courier_type).filter(Courier.id == courier_id)[0][0]

    regions = [region[0] for region in session.query(
        Region.region).outerjoin(
        CourierRegion, Region.id == CourierRegion.region_id).filter(
        CourierRegion.courier_id == courier_id)]

    working_hours = [time_to_string(wh) for wh in
                     session.query(CourierWorkingHour.start_time,
                                   CourierWorkingHour.end_time).filter(CourierWorkingHour.courier_id == courier_id)]
    courier_info['courier_type'] = type
    courier_info['regions'] = regions
    courier_info['working_hours'] = working_hours
    return courier_info


async def get_all_couriers(offset: int = 0, limit: int = 1):
    session = create_session()
    couriers_id = [courier_id[0] for courier_id in session.query(Courier.id)]

    couriers_info = {'couriers': [await get_courier_by_id(courier_id) for courier_id in couriers_id]}

    return couriers_info
