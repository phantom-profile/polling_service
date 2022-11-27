from backend.backend import BackendService


class MainWindow:
    def __init__(self, backend_service: BackendService, filename: str):
        self.backend_service = backend_service
        self.filename = filename

    def mainloop(self):
        self.register()
        self.listen_backend()

    def listen_backend(self):
        try:
            while True:
                polling_logs = self.backend_service.polling()
                for log in polling_logs:
                    self.write(log)
        except KeyboardInterrupt:
            self.write("Polling finished with keyboard interrupt")

    def register(self):
        logs = self.backend_service.register_senders(self.filename)
        for log in logs:
            self.write(log)

    def write(self, msg: str):
        print(msg, end='')
