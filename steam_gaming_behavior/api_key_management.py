from dotenv import load_dotenv
import pathlib
import os
import re
from .utils import clear_screen, countdown

def api_key_initialization():
    env_path = pathlib.Path('.env')

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        print("No .env file found.")

    api_key = os.getenv('API_KEY')

    if not api_key:
        print("Steam Web API key not found!")
        while True:
            api_key = input("Please enter your Steam Web API key:")
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