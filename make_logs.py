import logging
import sys


class Logger:
    def __init__(self) -> None:
        self.logger = logging.getLogger()

        self.handler_stdout = logging.StreamHandler(stream=sys.stdout)
        self.handler_to_file = logging.FileHandler("./in_work.log")
        self.formatter = logging.Formatter("[%(levelname)s] %d.%m.%Y %H:%M:%S %(message)s")

        self.handler_stdout.setFormatter(self.formatter)
        self.handler_to_file.setFormatter(self.formatter)

        self.logger.addHandler(self.handler_stdout)
        self.logger.addHandler(self.handler_to_file)

    def make_warn_log(self, message: str) -> None:
        self.logger.warning(message)

    def make_info_log(self, message: str) -> None:
        self.logger.info(message)
