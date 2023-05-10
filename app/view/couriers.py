from fastapi import HTTPException
from starlette import status

from app.database.__models import Courier, Region, CourierRegion, CourierWorkingHour
from app.database.db_session import create_session
from app.schemas.__couriers import CourierIds, PostCouriersModel, GetCourierModel, GetCouriersModel
from app.utils.time import time_to_string, split_time


async def post_couriers(couriers: PostCouriersModel) -> CourierIds:
    session = create_session()

    courier_ids = {'courier_ids': []}

    for courier in couriers.couriers:
        new_courier = Courier(courier_type=courier.courier_type)
        session.add(new_courier)
        session.commit()

        for region in courier.regions:
            region_id = list(session.query(Region).filter(Region.region == region))
            if not region_id:
                new_region = Region(region=region)
                session.add(new_region)
                session.commit()

                region_id = new_region.id
            else:
                region_id = region_id[0].id

            new_courier_region = CourierRegion(courier_id=new_courier.id, region_id=region_id)
            session.add(new_courier_region)
            session.commit()

        for cur_wh in courier.working_hours:
            start_time, end_time = split_time(cur_wh)

            new_wh = CourierWorkingHour(courier_id=new_courier.id, start_time=start_time, end_time=end_time)
            session.add(new_wh)
            session.commit()

        courier_ids['courier_ids'].append(new_courier.id)

    return CourierIds.parse_obj(courier_ids)


async def get_courier_by_id(courier_id: int) -> GetCourierModel:
    session = create_session()
    courier_info = {}

    courier_data = list(session.query(Courier).filter(Courier.id == courier_id))
    if not courier_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"There is no courier with id = {courier_id}")
    courier_type = courier_data[0].courier_type
    courier_regions = list(map(lambda data: data[0],
                               session.query(Region.region).
                               outerjoin(CourierRegion, Region.id == CourierRegion.region_id).
                               filter(CourierRegion.courier_id == courier_id)))
    courier_working_hours = list(map(lambda data: time_to_string([data[0], data[1]]),
                                     session.query(CourierWorkingHour.start_time, CourierWorkingHour.end_time).
                                     filter(CourierWorkingHour.courier_id == courier_id)))

    session.close()

    courier_info['courier_id'] = courier_id
    courier_info['courier_type'] = courier_type
    courier_info['regions'] = courier_regions
    courier_info['working_hours'] = courier_working_hours

    return GetCourierModel.parse_obj(courier_info)


async def get_all_couriers(limit: int = 1, offset: int = 0, courier_type=None) -> GetCouriersModel:
    session = create_session()
    couriers_info = {'couriers': []}

    couriers_data = session.query(Courier.id, Courier.courier_type).filter(offset <= Courier.id,
                                                                           Courier.id < offset + limit)
    if courier_type:
        couriers_data = couriers_data.filter(offset <= Courier.id, Courier.id < offset + limit).\
            filter(Courier.courier_type == courier_type)
    couriers_data = list(couriers_data)

    regions_data = list(session.query(CourierRegion.courier_id, Region.region).
                        outerjoin(CourierRegion, Region.id == CourierRegion.region_id).
                        filter(offset <= CourierRegion.courier_id,
                               CourierRegion.courier_id < offset + limit))
    working_hours_data = list(map(lambda data: (data[0], time_to_string([data[1], data[2]])),
                                  session.query(CourierWorkingHour.courier_id,
                                                CourierWorkingHour.start_time,
                                                CourierWorkingHour.end_time).
                                  filter(offset <= CourierWorkingHour.courier_id,
                                         CourierWorkingHour.courier_id < offset + limit)))
    session.close()

    for courier in couriers_data:
        courier_info = {}

        courier_regions = list(map(lambda data: data[1],
                                   filter(lambda data: data[0] == courier.id, regions_data)))
        courier_working_hours = list(map(lambda data: data[1],
                                         filter(lambda data: data[0] == courier.id, working_hours_data)))
        if not courier_regions:
            continue

        if not courier_working_hours:
            continue

        courier_info['courier_id'] = courier.id
        courier_info['courier_type'] = courier.courier_type
        courier_info['regions'] = courier_regions
        courier_info['working_hours'] = courier_working_hours

        couriers_info['couriers'].append(courier_info)

    return GetCouriersModel.parse_obj(couriers_info)
