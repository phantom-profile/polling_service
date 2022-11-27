from csv import DictReader
from typing import Iterable
from logging import getLogger, Logger, StreamHandler, Formatter, INFO, WARNING, ERROR

ERROR_CODE = 1


class MemoryStorage:
    def __init__(self):
        self.logs: list[str] = []

    def get_all(self):
        logs = self.logs.copy()
        self.logs.clear()
        return logs

    def add_new(self, record):
        self.logs.append(record)


class MemoryHandler(StreamHandler):
    def __init__(self, storage: MemoryStorage):
        StreamHandler.__init__(self)
        self.storage = storage

    def emit(self, record):
        msg = self.format(record)
        self.storage.add_new(msg)


class Loggable:
    __logger: Logger= None
    LOG_LEVEL = INFO

    def __init_logger(self):
        self.set_logger(getLogger(f"{self.__class__.__name__}Logger"))
        self.logger.setLevel(self.LOG_LEVEL)
        self.storage = MemoryStorage()
        handler = MemoryHandler(self.storage)
        formatter = Formatter('%(asctime)s | %(name)s::%(levelname)s - %(message)s\n')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, message: str, level=LOG_LEVEL):
        if not self.logger:
            self.__init_logger()

        self.logger.log(msg=message, level=level)

    def log_error(self, message: str):
        self.log(message=message, level=ERROR)

    def log_warning(self, message: str):
        self.log(message=message, level=WARNING)

    def log_exception(self, message: str):
        if not self.logger:
            self.__init_logger()

        self.logger.exception(msg=message)

    def logged_info(self) -> list[str]:
        if not self.logger:
            self.__init_logger()

        return self.storage.get_all()

    @property
    def logger(self):
        return self.__class__.__logger

    def set_logger(self, logger: Logger):
        self.__class__.__logger = logger


class CsvDownloader:
    @staticmethod
    def extract(filename: str) -> Iterable:
        with open(filename, 'r') as csv_file:
            data = list(DictReader(csv_file))
        return data
