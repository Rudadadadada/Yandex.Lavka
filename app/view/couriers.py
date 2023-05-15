import datetime

from fastapi import HTTPException
from starlette import status

from app.database.__models import Courier, Region, CourierRegion, CourierWorkingHour, DistributedOrders
from app.database.db_session import create_session
from app.schemas.__couriers import PostCouriersModel, GetCourierModel, GetCouriersModel, GetMetaInfoModel
from app.utils.time import split_time, HH_MM


async def post_couriers(couriers: PostCouriersModel) -> GetCouriersModel | None:
    session = create_session()

    couriers_info = {'couriers': []}

    for courier in couriers.couriers:
        new_courier = Courier(courier_type=courier.courier_type)
        session.add(new_courier)
        session.commit()

        for region in courier.regions:
            region_id = session.query(Region).filter(Region.region == region).all()
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

        couriers_info['couriers'].append({'courier_id': new_courier.id, 'courier_type': courier.courier_type,
                                          'regions': courier.regions, 'working_hours': courier.working_hours})

    return GetCouriersModel.parse_obj(couriers_info)


async def get_courier_by_id(courier_id: int) -> GetCourierModel:
    if courier_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    session = create_session()

    courier_data = session.query(Courier).filter(Courier.id == courier_id).all()

    if not courier_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    courier_type = courier_data[0].courier_type
    courier_regions = list(map(lambda data: data[0],
                               session.query(Region.region).
                               outerjoin(CourierRegion, Region.id == CourierRegion.region_id).
                               filter(CourierRegion.courier_id == courier_id)))
    courier_working_hours = list(map(lambda data: data[0].strftime(HH_MM) + '-' + data[1].strftime(HH_MM),
                                     session.query(CourierWorkingHour.start_time, CourierWorkingHour.end_time).
                                     filter(CourierWorkingHour.courier_id == courier_id)))

    session.close()

    courier_info = {'courier_id': courier_id, 'courier_type': courier_type, 'regions': courier_regions,
                    'working_hours': courier_working_hours}

    return GetCourierModel.parse_obj(courier_info)


async def get_all_couriers(limit: int = 1, offset: int = 0, courier_type: str = None) -> GetCouriersModel | None:
    if limit < 1 or offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    session = create_session()
    couriers_info = {'couriers': []}

    couriers_data = session.query(Courier.id, Courier.courier_type).filter(offset < Courier.id,
                                                                           Courier.id <= offset + limit)
    if courier_type:
        couriers_data = couriers_data.filter(Courier.courier_type == courier_type)
    couriers_data = couriers_data.all()
    regions_data = session.query(CourierRegion.courier_id, Region.region). \
        outerjoin(CourierRegion, Region.id == CourierRegion.region_id). \
        filter(offset < CourierRegion.courier_id,
               CourierRegion.courier_id <= offset + limit).all()
    working_hours_data = list(map(lambda data: (data[0], data[1].strftime(HH_MM) + '-' + data[2].strftime(HH_MM)),
                                  session.query(CourierWorkingHour.courier_id,
                                                CourierWorkingHour.start_time,
                                                CourierWorkingHour.end_time).
                                  filter(offset < CourierWorkingHour.courier_id,
                                         CourierWorkingHour.courier_id <= offset + limit)))
    session.close()

    for courier in couriers_data:
        courier_regions = list(map(lambda data: data[1],
                                   filter(lambda data: data[0] == courier.id, regions_data)))
        courier_working_hours = list(map(lambda data: data[1],
                                         filter(lambda data: data[0] == courier.id, working_hours_data)))
        if not courier_regions:
            continue
        if not courier_working_hours:
            continue

        courier_info = {'courier_id': courier.id, 'courier_type': courier.courier_type, 'regions': courier_regions,
                        'working_hours': courier_working_hours}

        couriers_info['couriers'].append(courier_info)

    return GetCouriersModel.parse_obj(couriers_info)


async def get_meta_info(courier_id: int, start_date: datetime.date, end_date: datetime.date) -> GetMetaInfoModel | None:
    courier_type_stat_coefficients = {'FOOT': [2, 3], 'BIKE': [3, 2], 'AUTO': [4, 1]}

    session = create_session()

    try:
        courier_info = await get_courier_by_id(courier_id)
    except HTTPException:
        return None

    if start_date == end_date:
        return None

    courier_type = courier_info.courier_type
    salary_coefficient, rating_coefficient = courier_type_stat_coefficients[courier_type]
    courier_data = session.query(DistributedOrders). \
        filter(start_date <= DistributedOrders.date, DistributedOrders.date < end_date). \
        filter(DistributedOrders.courier_id == courier_id). \
        filter(DistributedOrders.after_fact_time != None).all()

    salary = sum(list(map(lambda data: data.earnings, courier_data))) * salary_coefficient
    rating = (len(courier_data) / ((end_date - start_date).days * 24)) * rating_coefficient
    if not salary and not rating:
        return None

    meta_info = {'courier_id': courier_id, 'courier_type': courier_type,
                 'regions': courier_info.regions, 'working_hours': courier_info.working_hours,
                 'rating': rating, 'earnings': salary}

    return GetMetaInfoModel.parse_obj(meta_info)
