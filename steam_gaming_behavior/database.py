import sqlite3
import logging

from pandas import Timestamp
from .games import get_games
from .dotenv import write_into_dotenv
from datetime import datetime, timedelta

def connection(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    
    except sqlite3.Error as e:
        logging.critical(f"Error connecting to database: {e}")
        return None


def check_for_missing_tables(conn, required_tables):
    try:
        cursor = conn.cursor()

        # Checking for missing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {table[0] for table in cursor.fetchall()}

        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            logging.debug(f"Database is missing required tables: {missing_tables}")
        else:
            logging.debug(f"Database contains all required tables: {required_tables}")

        return missing_tables if missing_tables else None

    except sqlite3.Error as e:
        logging.critical(f"Error while checking for missing tables: {e}")
        conn.close()
        raise


def create_tables(conn, required_tables):
    try:
        cursor = conn.cursor()

        if "games_initial" in required_tables:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games_initial (
                appid INTEGER PRIMARY KEY,
                playtime_minutes INTEGER NOT NULL,
                name TEXT DEFAULT NULL,
                icon_hash TEXT DEFAULT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
            """)

        if "games_recent" in required_tables:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games_recent (
                appid INTEGER NOT NULL,
                playtime_minutes INTEGER NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                PRIMARY KEY (appid, checked_at)
            );
            """)

        conn.commit()
        logging.debug("Missing tables were created")
    
    except sqlite3.Error as e:
        logging.critical(f"Error during database initialization: {e}")
        conn.close()
        raise

def creation_and_initial_population_of_tables(tables, conn, steam_api_key, steam_id):
    logging.debug(f"Initializing missing tables: {tables}")

    # create missing tables
    create_tables(conn, tables)

    if "games_initial" in tables:
        all_games = get_games(steam_api_key, steam_id, get_all_owned_games=True)
        recent_games = get_games(steam_api_key, steam_id, get_all_owned_games=False)

        # combine all games and recent games for enriched data
        all_games_dict = {game.appid: game for game in all_games}

        # update entries with recent data if available
        for recent_game in recent_games:
            if recent_game.appid in all_games_dict:
                # enrich with name and icon_hash from recently played games
                all_games_dict[recent_game.appid].name = recent_game.name
                all_games_dict[recent_game.appid].icon_hash = recent_game.icon_hash
            else:
                # add recently played games not in all_games
                all_games_dict[recent_game.appid] = recent_game

        try:
            cursor = conn.cursor()

            # insert games to games_initial
            for game in all_games_dict.values():
                cursor.execute("""
                    INSERT INTO games_initial (appid, playtime_minutes, name, icon_hash, logged_at)
                    VALUES (?, ?, ?, ?, DATETIME(CURRENT_TIMESTAMP, '+1 hour'))
                    ON CONFLICT(appid) DO UPDATE SET 
                        playtime_minutes = excluded.playtime_minutes,
                        name = excluded.name,
                        icon_hash = excluded.icon_hash;
                """, (game.appid, game.playtime_minutes, game.name, game.icon_hash))

            conn.commit()
            logging.debug("Games data initialized successfully.")

        except sqlite3.Error as e:
            logging.error(f"Error inserting initial data: {e}")

def update_games_data(conn, data, env_path, timestamp=None):
    try:
        # Determine the timestamp to use
        if not timestamp:
            calculated_timestamp = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            timestamp = calculated_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            write_into_dotenv(env_path, "LAST_HOURLY_UPDATE", timestamp)

        cursor = conn.cursor()
        
        for game in data:
            cursor.execute("""
                SELECT playtime_minutes
                FROM games_initial
                WHERE appid = ?;
            """, (game.appid,))

            row = cursor.fetchone()

            updated_games_amt = 0

            # Game registered in games_initial
            if row:
                # Checking playtime for recently played against playtime total in games_initial to determine how long it was played
                initial_playtime = row[0]
                incremental_playtime = int(game.playtime_minutes) - initial_playtime

                # Inserting into games_recent if played recently
                if incremental_playtime > 0:
                    updated_games_amt += 1
                    cursor.execute("""
                        INSERT INTO games_recent (appid, playtime_minutes, checked_at)
                        VALUES (?, ?, ?)
                        ON CONFLICT(appid, checked_at) DO UPDATE SET
                            playtime_minutes = playtime_minutes + excluded.playtime_minutes;
                    """, (game.appid, incremental_playtime, timestamp))
                    logging.debug(f"{game.name} inserted or updated in games_recent table with timestamp: {timestamp}")

                    # Updating games_initial to hold most up-to-date data regarding total playtime
                    cursor.execute("""
                        UPDATE games_initial
                        SET playtime_minutes = ?, 
                            name = COALESCE(?, name), 
                            icon_hash = COALESCE(?, icon_hash)
                        WHERE appid = ?;
                    """, (game.playtime_minutes, game.name, game.icon_hash, game.appid))
                    logging.debug(f"Playtime for {game.name} was updated and saved into games_initial with timestamp: {timestamp}") 

            # Game not yet registered in games_initial
            else:
                updated_games_amt += 1

                # Inserting into games_initial
                cursor.execute("""
                    INSERT INTO games_initial (appid, playtime_minutes, name, icon_hash, logged_at)
                    VALUES (?, ?, ?, ?, ?);
                """, (game.appid, game.playtime_minutes, game.name, game.icon_hash, timestamp))
                logging.debug(f"{game.name} was encountered for the first time, saving into games_initial with timestamp: {timestamp}")

                # Checking if family shared game played previously but not in two weeks prior or entirely new game / not played family sharing game
                # Scenario no. 1 | Family sharing game played previously but not in two weeks prior
                if game.recently_played != game.playtime_minutes:
                    logging.debug(f"{game.name} is a family sharing game that was played before but not in past two weeks")
                    cursor.execute("""
                        INSERT INTO games_recent (appid, playtime_minutes, checked_at)
                        VALUES (?, ?, ?);
                    """, (game.appid, game.recently_played, timestamp))
                    logging.debug(f"{game.name} inserted into games_recent table with timestamp: {timestamp}") 
                # Scenario no. 2 | Entirely new game / not played family sharing game
                else:
                    logging.debug(f"{game.name} is a game bought after initial run of steam-gaming-behavior")
                    cursor.execute("""
                        INSERT INTO games_recent (appid, playtime_minutes, checked_at)
                        VALUES (?, ?, ?);
                    """, (game.appid, game.playtime_minutes, timestamp))
                    logging.debug(f"{game.name} inserted into games_recent table with timestamp: {timestamp}") 

        conn.commit()

        if updated_games_amt > 0:
            logging.info(f"{updated_games_amt} processed successfully with timestamp: {timestamp}")
        else:
            logging.info("No recently played games to process")

    except sqlite3.Error as e:
        logging.error(f"Error processing game updates: {e}")