import threading

from logger import Logger


class ExitListener:
    exit_flag = False

    @classmethod
    def listener_quit(cls):
        while not cls.get_exit_flag():
            result = input("Press 'q' to exit the program.\n")
            Logger.write_log(f"User input: {result}")

            if result == "q":
                cls.set_exit_flag(True)
                Logger.write_log("Exiting the program.")

    @classmethod
    def get_exit_flag(cls):
        return cls.exit_flag

    @classmethod
    def set_exit_flag(cls, flag):
        cls.exit_flag = flag

    @classmethod
    def start(cls):
        listener = threading.Thread(target=cls.listener_quit, daemon=True)
        listener.start()


if __name__ == "__main__":
    ExitListener.start()
    while not ExitListener.get_exit_flag():
        pass
