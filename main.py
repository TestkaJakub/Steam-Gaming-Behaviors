from datetime import datetime, timedelta
from steam_gaming_behavior import *
from threading import Thread
import logging
import time

def hourly_task(steam_api_key, steam_id, db_file, env_path):
    db_connection = connection(db_file)

    if db_connection:
        recent_games = get_games(steam_api_key, steam_id)
        update_games_data(db_connection, recent_games, env_path)
        write_into_dotenv(env_path, "LAST_SESSION_HOURLY_UPDATE_COMPLETION", True)
        db_connection.close()
    else:
        logging.error("Failed to connect to the database for hourly task.")
    
def schedule_round_hour_task(steam_api_key, steam_id, db_file, env_path):
    while True:
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        seconds_until_next_hour = (next_hour - now).total_seconds()

        logging.info(f"Sleeping until the next round hour ({next_hour})...")
        time.sleep(seconds_until_next_hour)

        print(f"Running task at {datetime.now()}")
        hourly_task(steam_api_key, steam_id, db_file, env_path)

def main():
    env_path, did_env_existed = get_or_create_dotenv()

    setup_logging(env_path, did_env_existed)

    steam_api_key = get_steam_api_key_and_save_into_dotenv(env_path)
    steam_id = get_steam_id_and_save_into_dotenv(env_path, steam_api_key)

    db_file = "steam_gaming_data.db"
    db_connection = connection(db_file)

    if not db_connection:
        logging.critical("Failed to establish a connection to the database. Exiting.")
        return

    required_tables = ["games_initial", "games_recent"]
    missing_tables = check_for_missing_tables(db_connection, required_tables)

    if missing_tables:
        creation_and_initial_population_of_tables(missing_tables, db_connection, steam_api_key, steam_id)

    last_startup_time_next_round_hour, last_hourly_update, was_last_hourly_update_completed = get_required_dotenv_fields(env_path)
    last_hour_update_correct_time = check_last_hour_update_correct_time(last_startup_time_next_round_hour, last_hourly_update, was_last_hourly_update_completed)
    
    # get games that user played previously but ended program before round hour
    recent_games = get_games(steam_api_key, steam_id)
    update_games_data(db_connection, recent_games, env_path, last_hour_update_correct_time)

    current_startup_time_next_round_hour(env_path)
    write_into_dotenv(env_path, "LAST_SESSION_HOURLY_UPDATE_COMPLETION", False)

    if db_connection:
        db_connection.close()

    round_hour_thread = Thread(target=schedule_round_hour_task, args=(steam_api_key, steam_id, db_file, env_path))
    round_hour_thread.daemon = True
    round_hour_thread.start()

    try:
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Exiting program.")

if __name__ == "__main__":
    main()
