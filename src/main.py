import threading
from datetime import datetime, timedelta
from time import sleep

from database import Database
from exit_listener import ExitListener
from logger import Logger
from settings import Settings
from steam import Steam

break_time_lock = threading.Lock()


def break_time(break_time_hours):
    with break_time_lock:

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

    database_thread = threading.Thread(target=update_database)
    steam_thread = threading.Thread(target=add_steam_games)

    database_thread.start()
    steam_thread.start()

    database_thread.join()
    steam_thread.join()

    Logger.write_log("Done!")


if __name__ == "__main__":
    main()
