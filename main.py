import time
from datetime import datetime, timedelta
from threading import Thread
from steam_gaming_behavior.initialization import initialize
from steam_gaming_behavior.gather import get_games
from steam_gaming_behavior.database import database_check, table_initialization, update_games_data

import sqlite3
import os

def fetch_and_process_games(api_key, steam_id, db_file):
    required_tables = ["games_initial", "games_recent"]

    db_connection, missing_tables = database_check(db_file, required_tables)

    if not db_connection:
        print("Failed to establish a connection to the database. Exiting.")
        return

    if missing_tables:
        table_initialization(missing_tables, db_connection, api_key, steam_id)

    process_recent_games(db_connection, api_key, steam_id)
    
    if db_connection:
        db_connection.close()

def process_recent_games(db_connection, api_key, steam_id):
    try:
        update_games_data(db_connection, api_key, steam_id)
        
    except Exception as e:
        print(f"Error fetching and processing games: {e}")

def midnight_task(api_key, steam_id, db_file):
    db_connection, _ = database_check(db_file, [])

    if db_connection:
        process_recent_games(db_connection, api_key, steam_id)
        db_connection.close()
    else:
        print("Failed to connect to the database for midnight task.")
    
def schedule_midnight_task(api_key, steam_id, db_file, interval=86400):
    while True:
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_midnight = (tomorrow - now).total_seconds()

        print(f"Sleeping until midnight ({seconds_until_midnight} seconds)...")
        time.sleep(seconds_until_midnight)

        print(f"Running scheduled task at midnight: {datetime.now()}")
        midnight_task(api_key, steam_id, db_file)


def main():
    api_key, steam_id = initialize()
    db_file = "steam_gaming_data.db"

    fetch_and_process_games(api_key, steam_id, db_file)

    midnight_thread = Thread(target=schedule_midnight_task, args=(api_key, steam_id, db_file))
    midnight_thread.daemon = True
    midnight_thread.start()

    try:
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Exiting program.")

if __name__ == "__main__":
    main()