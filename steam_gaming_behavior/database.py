import sqlite3
from .gather import get_games

def database_check(db_path, required_tables):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {table[0] for table in cursor.fetchall()}

        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            print(f"Database is missing required tables: {missing_tables}")
        else:
            print(f"Database contains all required tables: {required_tables}")

        return conn, missing_tables if missing_tables else None

    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None, required_tables

def create_tables(conn, required_tables):
    try:
        cursor = conn.cursor()

        if "games_initial" in required_tables:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games_initial (
                appid INTEGER PRIMARY KEY,
                playtime_minutes INTEGER,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

        if "games_recent" in required_tables:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games_recent (
                appid INTEGER PRIMARY KEY,
                name TEXT,
                playtime_minutes INTEGER,
                icon TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

        conn.commit()
        print("Missing tables were created")
    
    except sqlite3.Error as e:
        print(f"Error during database initialization: {e}")
        conn.close()
        raise

def table_initialization(tables, db_connection, api_key, steam_id):
    print(f"Initializing missing tables: {tables}")

    create_tables(db_connection, tables)

    if "games_initial" in tables:
        games = get_games(api_key, steam_id, get_all=True)
        try:
            cursor = db_connection.cursor()
            for game in games:
                cursor.execute("""
                INSERT INTO games_initial (appid, playtime_minutes)
                VALUES (?, ?)
                ON CONFLICT(appid) DO NOTHING;
                """, (game.appid, game.playtime_minutes))
            db_connection.commit()
            print("Initial data logged in the database.")
        except sqlite3.Error as e:
            print(f"Error inserting initial data: {e}")