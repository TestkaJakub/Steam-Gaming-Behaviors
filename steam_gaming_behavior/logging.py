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

def log_to_file_only(logger, message, level=logging.INFO):
    """
    Logs a message directly to the file handler without duplicating it in the console.
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            if handler.level <= level:
                logger.log(level, message, extra={"handler_only": handler})

def setup_logging(env_path, did_env_existed):
    valid_levels = {"CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, "WARNING": logging.WARNING, "INFO": logging.INFO, "DEBUG": logging.DEBUG}

    if not did_env_existed:
        console_level_prompt = (
            "It seems it's your first time using Steam Gaming Behaviors.\n"
            "What level of notifications would you like to see in the console? Default (3):"
        )
        console_level_options = {
            "1": "CRITICAL",
            "2": "ERROR",
            "3": "WARNING",
            "4": "INFO",
            "5": "DEBUG"
        }
        console_log_level = prompt_choice(console_level_prompt, console_level_options, "3")
        print(f"Chosen: {console_log_level} for console notifications")
        write_into_dotenv(env_path, "CONSOLE_LOG_LEVEL", console_log_level)

        file_level_prompt = (
            "What level of notifications would you like to save to the log file? Default (4):"
        )
        file_level_options = {
            "1": "CRITICAL",
            "2": "ERROR",
            "3": "WARNING",
            "4": "INFO",
            "5": "DEBUG"
        }
        file_log_level = prompt_choice(file_level_prompt, file_level_options, "4")
        print(f"Chosen: {file_log_level} for log file notifications")
        write_into_dotenv(env_path, "FILE_LOG_LEVEL", file_log_level)

    # Reload .env to ensure the latest values are loaded
    load_dotenv(env_path)

    # Read levels from environment
    console_log_level = os.getenv("CONSOLE_LOG_LEVEL", "WARNING")
    file_log_level = os.getenv("FILE_LOG_LEVEL", "INFO")

    # Validate levels
    if console_log_level not in valid_levels:
        print(f"Invalid CONSOLE_LOG_LEVEL '{console_log_level}' found in .env. Defaulting to 'WARNING'.")
        console_log_level = "WARNING"
    if file_log_level not in valid_levels:
        print(f"Invalid FILE_LOG_LEVEL '{file_log_level}' found in .env. Defaulting to 'INFO'.")
        file_log_level = "INFO"

    # Set up the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all logs; handlers will filter them

    # Create a formatter
    formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(valid_levels[console_log_level])
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("steam-gaming-behaviors.log", encoding="utf-8", mode="a")
    file_handler.setLevel(valid_levels[file_log_level])
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    try:
        logger.info(f"Logging initialized with console level '{console_log_level}' and file level '{file_log_level}'.")
    except Exception as e:
        print(f"Error setting up logging: {e}")
        raise
