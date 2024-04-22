from time import sleep
from database import Database
from steam import Steam


def main():
    while True:
        break_time = 1 * 60 * 60  # seconds

        Database.main()
        Steam.main()
        while break_time > 0:
            break_time -= 1
            print(f"Taking a break for {break_time} seconds ({round((
                  break_time / 60 / 60), 2)} hours)", end="\r")
            sleep(1)


if __name__ == "__main__":
    main()
