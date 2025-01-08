import os
import re
import logging

from .dotenv import write_into_dotenv
from .utils import clear_screen, countdown
from .logging import log_to_file_only

def get_steam_api_key_and_save_into_dotenv(env_path):
    api_key = os.getenv('API_KEY')

    # If steam api key not in dotenv get it from user and save into dotenv
    if not api_key:
        logging.debug("Steam Web API key not found!")
        api_key = ask_for_steam_api_key()
        write_into_dotenv(env_path, key="API_KEY", value=api_key)
        
    # If steam api key found in dotenv inform user
    else:
        logging.debug(f"Using API key from .env file.")

    # Return steam api key
    return api_key

def ask_for_steam_api_key():
    while True:
        logging.debug("Asking user for Steam Web API key")
        steam_api_key = input("Please enter your Steam Web API key: ")
        
        # return if steam api key is valid
        if steam_api_key_validation(steam_api_key):
            return steam_api_key
        
        #else try again
        logging.debug("Provided key '{steam_api_key}' is not valid. Printing info for user")
        print(f"Provided key '{steam_api_key}' is not valid.")
        countdown(3)
        clear_screen()
        print("Try again.")

def steam_api_key_validation(api_key):
    pattern = r'^[a-fA-F0-9]{32}$'
    is_provided_key_valid = re.fullmatch(pattern, api_key)
    return is_provided_key_valid