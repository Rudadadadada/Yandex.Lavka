import datetime
from typing import List

HH_MM = '%H:%M'


def split_time(time: str, to_intervals=False) -> List[str | datetime.datetime]:
    separated_time = time.split('-')
    start_time = separated_time[0]
    end_time = separated_time[1]
    if to_intervals:
        start_time = datetime.datetime.strptime(start_time, HH_MM)
        end_time = datetime.datetime.strptime(end_time, HH_MM)
    return [start_time, end_time]
