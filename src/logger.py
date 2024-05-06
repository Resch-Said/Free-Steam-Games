from datetime import datetime


class Logger:

    @classmethod
    def write_log(cls, message, print_message=True, log_file=False):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if print_message:
            print(message)

        if log_file:
            with open("../log.txt", "a") as file:
                file.write(current_time + ": " + message + "\n")
