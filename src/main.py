from time import sleep

from database import Database
from src.chrome_driver_manager import ChromeDriverManager
from steam import Steam


def main():
    while True:
        break_time = 8 * 60 * 60  # seconds

        ChromeDriverManager().main()
        Database.main()
        Steam.main()
        while break_time > 0:
            break_time -= 1
            print(
                f"Taking a break for {break_time} seconds ({round((break_time / 60 / 60), 2)} hours)",
                end="\r",
            )
            sleep(1)


# TODO: Show how many games are left to be checked
if __name__ == "__main__":
    main()
