def time_to_string(time) -> str:
    start_time = str(time[0].hour).rjust(2, '0') + ':' + str(time[0].minute).rjust(2, '0')
    end_time = str(time[1].hour).rjust(2, '0') + ':' + str(time[1].minute).rjust(2, '0')
    return start_time + '-' + end_time
