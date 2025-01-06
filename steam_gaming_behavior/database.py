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
                name TEXT DEFAULT NULL,
                icon TEXT DEFAULT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

        if "games_recent" in required_tables:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games_recent (
                appid INTEGER,
                playtime_minutes INTEGER,
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

    # Create missing tables
    create_tables(db_connection, tables)

    if "games_initial" in tables:
        all_games = get_games(api_key, steam_id, get_all=True)
        recent_games = get_games(api_key, steam_id, get_all=False)

        # Combine all games and recent games for enriched data
        all_games_dict = {game.appid: game for game in all_games}

        # Update entries with recent data if available
        for recent_game in recent_games:
            if recent_game.appid in all_games_dict:
                # Enrich with name and icon from recently played games
                all_games_dict[recent_game.appid].name = recent_game.name
                all_games_dict[recent_game.appid].icon = recent_game.icon
            else:
                # Add recently played games not in all_games
                all_games_dict[recent_game.appid] = recent_game

        try:
            cursor = db_connection.cursor()

            # Insert or update all games in the database
            for game in all_games_dict.values():
                cursor.execute("""
                    INSERT INTO games_initial (appid, playtime_minutes, name, icon)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(appid) DO UPDATE SET 
                        playtime_minutes = excluded.playtime_minutes,
                        name = excluded.name,
                        icon = excluded.icon;
                """, (game.appid, game.playtime_minutes, game.name, game.icon))

            db_connection.commit()
            print("Games data initialized successfully.")

        except sqlite3.Error as e:
            print(f"Error inserting initial data: {e}")

def update_games_data(db_connection, api_key, steam_id):
    recent_games = get_games(api_key, steam_id, get_all=False)
    try:
        cursor = db_connection.cursor()

        for game in recent_games:
            cursor.execute("""
                SELECT playtime_minutes
                FROM games_initial
                WHERE appid = ?;
            """, (game.appid,))

            row = cursor.fetchone()
            
            if row:
                initial_playtime = row[0]
                incremental_playtime = game.playtime_minutes - initial_playtime

                if incremental_playtime > 0:
                    cursor.execute("""
                        INSERT INTO games_recent (appid, playtime_minutes, checked_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP);
                    """, (game.appid, incremental_playtime))

                cursor.execute("""
                    UPDATE games_initial
                    SET playtime_minutes = ?
                    WHERE appid = ?;
                """, (game.playtime_minutes, game.appid))
            else:
                cursor.execute("""
                    INSERT INTO games_initial (appid, playtime_minutes, name, icon)
                    VALUES (?, ?, ?, ?)
                """, (game.appid, game.playtime_minutes, game.name, game.icon))

                if game.recently_played != game.playtime_forever:
                    cursor.execute("""
                        INSERT INTO games_recent (appid, playtime_minutes, checked_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP);
                    """, (game.appid, game.recently_played))
                else:
                    cursor.execute("""
                        INSERT INTO games_recent (appid, playtime_minutes, checked_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP);
                    """, (game.appid, game.playtime_minutes))

        db_connection.commit()
        print("Games processed successfully.")

    except sqlite3.Error as e:
        print(f"Error processing game updates: {e}")