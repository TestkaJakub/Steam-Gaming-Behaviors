from dotenv import load_dotenv
import pathlib
from .utils import clear_screen

def get_or_create_dotenv():
    env_path = pathlib.Path('.env')
    already_existed = True

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        already_existed = False
        print("No .env file found.")

    return env_path, already_existed

def write_into_dotenv(env_path, key, value):
    # Read existing .env content
    env_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_lines = f.readlines()

    # Update or append the key-value pair
    key_found = False
    updated_lines = []
    for line in env_lines:
        if line.strip().startswith(f"{key}="):
            updated_lines.append(f"{key}={value}\n")
            key_found = True
        else:
            updated_lines.append(line)

    if not key_found:
        updated_lines.append(f"{key}={value}\n")

    # Write the updated content back to .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    clear_screen()
    print(f"{key} saved to {env_path}.")