from typing import Protocol

from backend.senders import PackageSender, SendersFactory
from backend.utils import Loggable, CsvDownloader


class BackendService(Protocol):
    def polling(self) -> list[str]: ...

    def register_senders(self, from_csv: str) -> list[str] | None: ...


class PollingQueue(Loggable):
    def __init__(self):
        self.senders: list[PackageSender] = []
        self.perform_polling: bool = True

    def polling(self) -> list[str]:
        logs = []
        for sender in self.senders:
            sender.send_packages()
            if sender.job_performed:
                logs += sender.logged_info()
        return logs

    def register_senders(self, *senders: PackageSender):
        self.clean_queue()
        for sender in senders:
            self.senders.append(sender)

    def clean_queue(self):
        self.senders.clear()


class PollingService:
    def __init__(self):
        self.csv_downloader = CsvDownloader()
        self.senders_factory = SendersFactory()
        self.polling_queue = PollingQueue()

    def polling(self) -> list[str]:
        return self.polling_queue.polling()

    def register_senders(self, from_csv: str) -> list[str]:
        data = self.csv_downloader.extract(from_csv)
        senders = self.senders_factory.create_senders_from_csv(data)
        logs = self.senders_factory.logged_info()
        if len(logs):
            return ['Csv download failed!\n'] + logs

        self.polling_queue.register_senders(*senders)
        return ['Senders registered successfully. Ready for polling\n']
