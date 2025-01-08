import time
import os
import logging

def countdown(seconds):
    for i in range(seconds, 0, -1):
        logging.debug(f"Waiting: {i} seconds...")
        time.sleep(1)
    clear_screen()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')