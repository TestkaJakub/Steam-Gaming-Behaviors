import os
from .dotenv import write_into_dotenv
from datetime import datetime, timedelta

def get_required_dotenv_fields(env_path):
    last_startup_time_next_round_hour = os.getenv("LAST_STARTUP_NEXT_ROUND_HOUR")
    last_hourly_update = os.getenv("LAST_HOURLY_UPDATE")
    was_last_hourly_update_completed = os.getenv("LAST_SESSION_HOURLY_UPDATE_COMPLETION")

    if not last_startup_time_next_round_hour:
        current_startup_time_next_round_hour(env_path)

    return last_startup_time_next_round_hour, last_hourly_update, was_last_hourly_update_completed

def check_last_hour_update_correct_time(was_last_hourly_update_completed, last_hourly_update, last_startup_time_next_round_hour):
    if was_last_hourly_update_completed:
        last_hourly_update_dt = datetime.strptime(last_hourly_update, "%Y-%m-%d %H:%M:%S")
        corrected_time = last_hourly_update_dt + timedelta(hours=1)
        return corrected_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return last_startup_time_next_round_hour
    
def current_startup_time_next_round_hour(env_path):
    now = datetime.now()
    next_round_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    sqlite_timestamp = next_round_hour.strftime("%Y-%m-%d %H:%M:%S")

    write_into_dotenv(env_path, "LAST_STARTUP_NEXT_ROUND_HOUR", sqlite_timestamp)