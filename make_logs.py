import logging
import sys


class Logger:
    def __init__(self) -> None:
        self.logger_info = logging.getLogger()
        self.logger_warn = logging.getLogger()
        self.logger_info.setLevel(logging.DEBUG)
        self.logger_warn.setLevel(logging.DEBUG)

        self.stdout_stream = logging.StreamHandler(sys.stdout)
        self.file_stream = logging.FileHandler("in_work.log", encoding="utf-8")
        self.format = logging.Formatter(datefmt="%d_%m_%Y %I:%M:%S", fmt="%(asctime)s [%(levelname)s]: %(message)s")

        self.stdout_stream.setFormatter(self.format)
        self.file_stream.setFormatter(self.format)

        self.logger_warn.addHandler(self.stdout_stream)
        self.logger_warn.addHandler(self.file_stream)
        self.logger_info.addHandler(self.stdout_stream)
        self.logger_info.addHandler(self.file_stream)

    def make_warn_log(self, message: str) -> None:
        self.logger_warn.warning(message)

    def make_info_log(self, message: str) -> None:
        self.logger_info.info(message)
