from dotenv import load_dotenv
import pathlib
from .utils import clear_screen

def get_or_create_dotenv():
    env_path = pathlib.Path('.env')

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        print("No .env file found.")

    return env_path

def write_into_dotenv(env_path, key, value):
    with open(env_path, 'a') as f:
        f.write(f"{key}={value}\n")
    clear_screen()
    print(f"{key} saved to {env_path}.")