import threading
from time import sleep

from database import Database
from exit_listener import ExitListener
from steam import Steam


def main():
    ExitListener.start()

    while True:
        break_time = 8 * 60 * 60  # seconds
        if ExitListener.get_exit_flag():
            break

        Database.main()
        Steam.main()

        print("Done!")
        while break_time > 0:
            if ExitListener.get_exit_flag():
                break

            break_time -= 1
            print(
                f"Taking a break for {break_time} seconds ({round((break_time / 60 / 60), 2)} hours)",
                end="\r",
            )
            sleep(1)

    input("Press Enter to close...")


if __name__ == "__main__":
    main()
