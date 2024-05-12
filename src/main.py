from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime, timedelta
from time import sleep

from database import Database
from exit_listener import ExitListener
from logger import Logger
from settings import Settings
from steam import Steam



def break_time(break_time_hours):
    end_time = datetime.now() + timedelta(hours=break_time_hours)

    Logger.write_log(
        f"Taking a break for {break_time_hours} hours. Ending at {str(end_time).split('.')[0]}"
    )

    while datetime.now() < end_time:
        if ExitListener.get_exit_flag():
            break
        sleep(1)


def add_steam_games():
    while not ExitListener.get_exit_flag():
        Steam.main()
        break_time(break_time_hours=8)


def update_database():
    while not ExitListener.get_exit_flag():
        Database.main()
        break_time(break_time_hours=0.1)


def main():
    ExitListener.start()
    Logger.write_log(f"Current Version: {Settings.get_software_version()}")

    if not Steam.check_if_user_is_logged_in():
        Steam.open_steam_login_page()
        
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(update_database)
        executor.submit(add_steam_games)

    Logger.write_log("Done!")


if __name__ == "__main__":
    main()
