from datetime import datetime


class Logger:

    @classmethod
    def write_log(cls, message, print_message=True):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if print_message:
            print(message)
        with open("../log.txt", "a") as file:
            file.write(current_time + ": " + message + "\n")
