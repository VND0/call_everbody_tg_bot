import logging
import sys


class Logger:
    def __init__(self) -> None:
        self.logger_info = logging.getLogger()
        self.logger_warn = logging.getLogger()

        self.handler_stdout_warn = logging.StreamHandler(stream=sys.stdout)
        self.handler_to_file_warn = logging.FileHandler("in_work.log")
        self.handler_stdout_info = logging.StreamHandler(stream=sys.stdout)
        self.handler_to_file_info = logging.FileHandler("in_work.log")

        self.formatter_info = logging.Formatter("[INFO] %d.%m.%Y %H:%M:%S %(message)s")
        self.formatter_warn = logging.Formatter("[WARNING] %d.%m.%Y %H:%M:%S %(message)s")

        self.handler_stdout_warn.setFormatter(self.formatter_warn)
        self.handler_to_file_warn.setFormatter(self.formatter_warn)
        self.handler_stdout_info.setFormatter(self.formatter_info)
        self.handler_to_file_info.setFormatter(self.formatter_info)

        self.logger_warn.addHandler(self.handler_stdout_warn)
        self.logger_warn.addHandler(self.handler_to_file_warn)
        self.logger_info.addHandler(self.handler_stdout_info)
        self.logger_info.addHandler(self.handler_to_file_info)

        self.logger_info.level = logging.INFO
        self.logger_warn.level = logging.WARNING

    def make_warn_log(self, message: str) -> None:
        self.logger_warn.warning(message)

    def make_info_log(self, message: str) -> None:
        self.logger_info.info(message)
