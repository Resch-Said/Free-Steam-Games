from datetime import datetime


class Logger:

    @classmethod
    def write_log(cls, message, print_message=True, log_file=False):
        if print_message:
            try:
                print(message)
            except UnicodeEncodeError:
                print(message.encode("utf-8"))

        if log_file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("../log.txt", "a") as file:
                file.write(current_time + ": " + message + "\n")
