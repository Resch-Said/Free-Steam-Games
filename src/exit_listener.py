from time import sleep

import keyboard


class ExitListener:
    exit_flag = False

    @classmethod
    def listener_quit(cls):
        while True:
            if keyboard.read_key() == "q" or keyboard.read_key() == "Q":
                print("Finishing current task before exiting.")
                cls.exit_flag = True
                break
            sleep(1)

    @classmethod
    def get_exit_flag(cls):
        return cls.exit_flag
