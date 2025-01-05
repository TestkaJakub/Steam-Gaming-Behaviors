from steam_gaming_behavior.initialization import initialize
from steam_gaming_behavior.gather import get_games

def main():
    api_key, steam_id = initialize()

    print(get_games(api_key, steam_id))
    get_games(api_key, steam_id, True)

if __name__ == "__main__":
    main()