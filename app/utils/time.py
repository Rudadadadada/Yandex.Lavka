from datetime import datetime
from typing import List


def time_to_string(time: datetime.time) -> str:
    start_time = str(time[0].hour).rjust(2, '0') + ':' + str(time[0].minute).rjust(2, '0')
    end_time = str(time[1].hour).rjust(2, '0') + ':' + str(time[1].minute).rjust(2, '0')
    return start_time + '-' + end_time


def split_time(time: str) -> List[str]:
    separated_time = time.split('-')
    start_time = separated_time[0]
    end_time = separated_time[1]
    return [start_time, end_time]


def get_minutes_from_string(time: str) -> int:
    hours, minutes = map(int, time.split(':'))
    return hours * 60 + minutes


def get_minutes_from_interval_string(time: str) -> int:
    start_time, end_time = split_time(time)
    start = get_minutes_from_string(start_time)
    end = get_minutes_from_string(end_time)
    return end - start
