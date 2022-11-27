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
import sys

from console_main_window import MainWindow
from backend.backend import BackendService, PollingService


class Application:
    def __init__(self, backend_service: BackendService, filename: str):
        self.interface = MainWindow(backend_service=backend_service, filename=filename)

    def launch(self):
        self.interface.mainloop()


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input('Enter path to csv file\n')

    app = Application(backend_service=PollingService(), filename=filename)
    app.launch()


if __name__ == '__main__':
    main()
