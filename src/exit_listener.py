from pynput import keyboard


class ExitListener:
    exit_flag = False

    @classmethod
    def on_press(cls, key):
        try:
            if key.char == "q":
                cls.set_exit_flag(True)
                print("\nExiting the program. Please wait...")
        except AttributeError:
            pass

    @classmethod
    def listener_quit(cls):
        listener = keyboard.Listener(on_press=cls.on_press)
        listener.start()

    @classmethod
    def get_exit_flag(cls):
        return cls.exit_flag

    @classmethod
    def set_exit_flag(cls, flag):
        cls.exit_flag = flag
