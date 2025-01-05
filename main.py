from steam_gaming_behavior.initialization import initialize
from steam_gaming_behavior.gather import get_games
from steam_gaming_behavior.database import database_check, table_initialization

import sqlite3
import os

def main():
    # Initialization (getting api_key and steam_id)
    api_key, steam_id = initialize()

    db_file = "steam_gaming_data.db"
    required_tables = ["games_initial", "games_recent"]

    # Establishing Database
    db_connection, missing_tables = database_check(db_file, required_tables)

    if not db_connection:
        print("Failed to establish a connection to the database. Exiting.")
        return
    
    # Initialize missing tables
    if missing_tables:
        table_initialization(missing_tables, db_connection, api_key, steam_id)
    
    print("WIP")

    if db_connection:
        db_connection.close()
    # If exists get recently played games

    # print(get_games(api_key, steam_id))

if __name__ == "__main__":
    main()