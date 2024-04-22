import threading
from time import sleep

from chrome_driver_manager import ChromeDriverManager
from database import Database
from steam import Steam
from exit_listener import ExitListener

exit_flag = False


def main():
    listener_thread = threading.Thread(target=ExitListener.listener_quit)
    listener_thread.start()
    print("Press 'q' to exit the program.")

    while True:
        if ExitListener.get_exit_flag():
            break

        break_time = 8 * 60 * 60  # seconds

        ChromeDriverManager().main()
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


# TODO: Show how many games are left to be checked
if __name__ == "__main__":
    main()
