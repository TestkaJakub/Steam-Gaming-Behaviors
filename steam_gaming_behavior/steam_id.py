import os
import urllib3
import json
import logging

from .dotenv import write_into_dotenv
from .utils import countdown, clear_screen

def get_steam_id_and_save_into_dotenv(env_path, api_key):
    steam_id = os.getenv('STEAM_ID')

    # If steam id not in dotenv get it from user and save into dotenv
    if not steam_id:
        logging.debug("Steam ID not found!")
        steam_id = ask_for_steam_id(api_key)
        write_into_dotenv(env_path, key="STEAM_ID", value=steam_id)
    
    # If steam id found in dotenv inform user
    else:
        logging.debug(f"Using Steam ID from .env file.")

    # Return steam id
    return steam_id

def ask_for_steam_id(api_key):
    while True:
        while True:
            option = ask_for_preferred_method_of_steam_id_setting_up()

            match option:
                case "1": # Input steam id directly
                    logging.debug("Asking user for Steam ID")
                    steam_id = input("Please enter your Steam ID: ")

                    break
                case "2": # Get steam id based on steam vanity url
                    logging.debug("Asking user for Steam vanity URL")
                    steam_vanity_url = input("Please enter your Steam vanity URL")
                    steam_id = request_steam_id_from_steam_vanity_url(api_key, steam_vanity_url)
                    break
                case _: # Incorrect method of steam id setting up
                    logging.debug("Incorrect preferred method of setting up the Steam ID")
                    print(f"Incorrect method '{option}', please try again")
    
        # return if steam id is valid
        if steam_id_validation(steam_id):
            return steam_id
        
        # else try again
        countdown(3)
        print("Try again.")

def ask_for_preferred_method_of_steam_id_setting_up():
    logging.debug("Asking user for preferred method of setting up the Steam ID")
    print("""Please choose preferred method of setting up the Steam ID (1 or 2)
        1) Direct Steam ID insertion
        2) Determine Steam ID based on steam vanity URL
    """)
    option = input()

    clear_screen()

    return option

def request_steam_id_from_steam_vanity_url(api_key, steam_vanity_url):
    request = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}".format(api_key, steam_vanity_url)
    response = urllib3.request("GET", request).data
    decoded_response = response.decode('utf-8')
    response_dict = json.loads(decoded_response)
    steam_id = response_dict['response']['steamid']
    return steam_id

def steam_id_validation(steam_id):
    if not steam_id.isdigit():
        logging.debug(f"Provided Steam ID '{steam_id}' is not valid. Must be numeric.")
        return False
    if not (len(steam_id) == 17):
        logging.debug(f"Steam ID '{steam_id}' must be 17 characters long.")
        return False
    return True