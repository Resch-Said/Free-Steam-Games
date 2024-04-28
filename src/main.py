import threading
from datetime import datetime, timedelta
from time import sleep

from database import Database
from exit_listener import ExitListener
from settings import Settings
from steam import Steam

break_time_lock = threading.Lock()


def break_time(break_time_hours=8):
    with break_time_lock:
        if break_time_hours <= 1:
            break_time_hours = 1.01

        end_time = datetime.now() + timedelta(hours=break_time_hours)
        print(
            "\r",
            f"Taking a break for {break_time_hours} hours. Ending at {str(end_time).split('.')[0]}",
        )

    while datetime.now() < end_time:
        if ExitListener.get_exit_flag():
            break
        sleep(1)


def add_steam_games():
    while True:
        Steam.main()
        if ExitListener.get_exit_flag():
            break
        break_time()


def update_database():
    while True:
        Database.main()
        if ExitListener.get_exit_flag():
            break
        break_time()


def main():
    ExitListener.start()
    print(f"Current Version: {Settings.get_software_version()}")

    if not Steam.check_if_user_is_logged_in():
        Steam.open_steam_login_page()

    database_thread = threading.Thread(target=update_database)
    steam_thread = threading.Thread(target=add_steam_games)

    database_thread.start()
    steam_thread.start()

    database_thread.join()
    steam_thread.join()

    print("Done!")


if __name__ == "__main__":
    main()
