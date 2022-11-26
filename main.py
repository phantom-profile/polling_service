# BACKEND (Scapy + python)
# get info from csv (csv)
# create queue for senders with their params (Redis?)
# once per N time execute sending (while True loop)
# logging (logger)
#
# FRONTEND (Tkinter)
# form for download file
# button START POLLING
# text field for system errors
# button for stop polling
#
# INFRASTRUCTURE
# doker container
# simple linux system
# python 3.10 + venv
#
import os

from frontend import MainWindow
from backend.backend import BackendService, PollingService


class Application:
    def __init__(self, backend_service: BackendService):
        self.interface = MainWindow(
            'TCP/UDP/ICMP polling service',
            geometry='850x400',
            backend_service=backend_service,
            welcome_message='Download CSV file and start polling. See "CSV format Hint" to check CSV rules.'
        )

    def launch(self):
        self.interface.mainloop()


def main():
    app = Application(backend_service=PollingService())
    app.launch()


if __name__ == '__main__':
    main()
