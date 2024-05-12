import threading
from datetime import datetime, timedelta
from time import sleep
import asyncio

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


async def add_steam_games():
    while not ExitListener.get_exit_flag():
        Steam.main()
        break_time(break_time_hours=8)


async def update_database():
    while not ExitListener.get_exit_flag():
        Database.main()
        break_time(break_time_hours=0.1)


async def main():
    ExitListener.start()
    Logger.write_log(f"Current Version: {Settings.get_software_version()}")

    if not Steam.check_if_user_is_logged_in():
        Steam.open_steam_login_page()

    tasks = [add_steam_games(), update_database()]

    await asyncio.gather(*tasks)

    Logger.write_log("Done!")


if __name__ == "__main__":
    asyncio.run(main())
