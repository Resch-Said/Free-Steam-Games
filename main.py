from time import sleep

from src.database import Database
from src.exit_listener import ExitListener
from src.steam import Steam


def main():
    ExitListener.start()

    while True:
        if ExitListener.get_exit_flag():
            break

        break_time = 8 * 60 * 60  # seconds

        if ExitListener.get_exit_flag():
            break

        Database.main()
        if ExitListener.get_exit_flag():
            break

        Steam.main()
        while break_time > 0:
            if ExitListener.get_exit_flag():
                break

            break_time -= 1
            print(
                f"Taking a break for {break_time} seconds ({round((break_time / 60 / 60), 2)} hours)",
                end="\r",
            )
            sleep(1)
    print("Done!")


if __name__ == "__main__":
    main()
