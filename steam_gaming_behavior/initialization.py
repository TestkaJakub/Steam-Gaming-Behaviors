from dotenv import load_dotenv
import pathlib
import os
import re
from .utils import clear_screen, countdown
import urllib3
import json

def environment_initialization():
    env_path = pathlib.Path('.env')

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        print("No .env file found.")

    return env_path

def initialize():
    env_path = environment_initialization()
    api_key = api_key_initialization(env_path)
    steam_id = steam_id_initialization(env_path, api_key)

    return api_key, steam_id

def api_key_initialization(env_path):
    api_key = os.getenv('API_KEY')

    if not api_key:
        print("Steam Web API key not found!")
        while True:
            api_key = input("Please enter your Steam Web API key: ")
            if api_key_validation(api_key):
                with open(env_path, 'a') as f:
                    f.write(f"API_KEY={api_key}\n")
                clear_screen()
                print(f"API key saved to {env_path}.")
                break
            countdown(3)
            print("Try again.")
    else:
        print(f"Using API key from .env file.")

    return api_key

def api_key_validation(key):
    pattern = r'^[a-fA-F0-9]{32}$'
    is_provided_key_valid = re.fullmatch(pattern, key)
    if not is_provided_key_valid:
        print(f"Provided key '{key}' is not valid.")
    return is_provided_key_valid

def steam_id_initialization(env_path, key):
    steam_id = os.getenv('STEAM_ID')

    if not steam_id:
        print("Steam ID not found!")
        while True:
            while True:
                print("""Please choose preferred method of setting up the Steam ID (1 or 2)
                1) Direct Steam ID insertion
                2) Determine Steam ID based on steam vanity URL
                """)
                option = input()

                clear_screen()
                match option:
                    case "1":
                        steam_id = input("Please enter your Steam ID: ")
                        break
                    case "2":
                        steam_vanity_url = input("Please enter your Steam vanity URL")
                        request = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}".format(key, steam_vanity_url)
                        response = urllib3.request("GET", request).data
                        decoded_response = response.decode('utf-8')
                        response_dict = json.loads(decoded_response)
                        steam_id = response_dict['response']['steamid']
                        break
                    case _:
                        print(f"Incorrect method '{option}', please try again")
                    # ResolveVanityURL
           
            if steam_id_validation(steam_id):
                with open(env_path, 'a') as f:
                    f.write(f"STEAM_ID={steam_id}\n")
                clear_screen()
                print(f"Steam ID saved to {env_path}.")
                break
            countdown(3)
            print("Try again.")
    else:
        print(f"Using Steam ID from .env file.")

    return steam_id

def steam_id_validation(steam_id):
    # Assuming Steam IDs are numeric (adjust as needed based on requirements)
    if not steam_id.isdigit():
        print(f"Provided Steam ID '{steam_id}' is not valid. Must be numeric.")
        return False
    if not (len(steam_id) == 17):  # Example length constraints
        print(f"Steam ID '{steam_id}' must be 17 characters long.")
        return False
    return True
