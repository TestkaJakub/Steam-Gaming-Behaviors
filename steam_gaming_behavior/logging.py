import os
import logging
from dotenv import load_dotenv
from .dotenv import write_into_dotenv

def prompt_choice(prompt, options, default):
    print(prompt)
    for key, value in options.items():
        print(f"  {key}) {value}")
    choice = input().strip()
    return options.get(choice, options[default])

def setup_logging(env_path, did_env_existed):
    valid_levels = {"CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, "WARNING": logging.WARNING, "INFO": logging.INFO}

    if not did_env_existed:
        notification_prompt = (
            "It seems it's your first time using steam gaming behaviors.\n"
            "What is your preferred program notification level, default (4)?"
        )
        notification_options = {
            "1": "CRITICAL",
            "2": "ERROR",
            "3": "WARNING",
            "4": "INFO"
        }
        log_level = prompt_choice(notification_prompt, notification_options, "4")
        print(f"Chosen: {log_level} notifications")
        write_into_dotenv(env_path, "LOG_LEVEL", log_level)

        destination_prompt = (
            "Do you prefer to see notifications directly in the console or saved to a log, default (2)?"
        )
        destination_options = {
            "1": "LOG_FILE",
            "2": "CONSOLE"
        }
        log_destination = prompt_choice(destination_prompt, destination_options, "2")
        print(f"Chosen: {'log file' if log_destination == 'LOG_FILE' else 'console'}")
        write_into_dotenv(env_path, "LOGGING_DESTINATION", log_destination)

    # Reload .env to ensure the latest values are loaded
    load_dotenv(env_path)

    # Read the log level and destination from the environment
    log_level = os.getenv("LOG_LEVEL", "INFO")
    print(f"DEBUG: Loaded log level from .env: {log_level}")  # Debugging message
    log_destination = os.getenv("LOGGING_DESTINATION", "CONSOLE")
    print(f"DEBUG: Loaded log destination from .env: {log_destination}")  # Debugging message

    # Validate log level
    if log_level not in valid_levels:
        print(f"Invalid LOG_LEVEL '{log_level}' found in .env. Defaulting to 'INFO'.")
        log_level = "INFO"

    logging_config = {
        "level": valid_levels[log_level],
        "format": "{asctime} - {levelname} - {message}",
        "style": "{",
        "datefmt": "%Y-%m-%d %H:%M",
    }

    if log_destination == "LOG_FILE":
        logging_config.update({
            "filename": "steam-gaming-behaviors.log",
            "encoding": "utf-8",
            "filemode": "a",
        })

    try:
        logging.basicConfig(**logging_config)
        logging.info(f"Logging initialized with level '{log_level}' and destination '{log_destination}'.")
    except Exception as e:
        print(f"Error setting up logging: {e}")
        raise
