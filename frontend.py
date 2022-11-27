from tkinter import filedialog, Frame, Tk, Button, scrolledtext, INSERT, LEFT, BOTTOM, TOP, END
from tkinter.messagebox import showinfo
from typing import Callable

from backend.backend import BackendService


class MainWindow(Tk):
    DESTINATION = 'dst.ip'
    PORT = 'dst.port'
    PACKAGES = 'packages'
    COOLDOWN = 'cooldown'
    PROTOCOL = 'service'

    def __init__(self, title: str, geometry: str, backend_service: BackendService, welcome_message: str):
        super().__init__()
        self.title(title)
        self.geometry(geometry)
        self.buttons = Frame(self)
        self.output = scrolledtext.ScrolledText(self, font=('consolas', '12'))
        self.write(welcome_message)
        self.objects = {}
        self.backend_service = backend_service
        self.session_status = {
            'filename': '',
            'polling': False
        }

        self.configure_layouts()
        self.create_buttons()

    def configure_layouts(self):
        self.buttons.pack(side=TOP, fill="both", expand=False, pady=20)
        self.output.pack(side=BOTTOM, fill='both', expand=True)

    def create_buttons(self):
        self.add('hint', self.button_factory(text="CSV format hint", bg='lightblue', command=self.show_hint))
        self.add('open', self.button_factory(text='Open a CSV File', command=self.select_file))
        self.add('start', self.button_factory(text="Start Polling", bg="lightgreen", command=self.service_start))
        self.add('stop', self.button_factory(text="Stop Polling", bg="red", command=self.service_stop))
        self.add('clear', self.button_factory(text='Clear journal', bg='red', command=self.clear_journal))

    def get_object(self, id: str):
        return self.objects[id]

    def add(self, id: str, element):
        self.objects[id] = element

    def button_factory(self, text: str, command: Callable, bg: str = 'grey') -> Button:
        button = Button(self.buttons, width=15, text=text, command=command, bg=bg)
        button.pack(side=LEFT, padx=10)
        return button

    def service_start(self):
        self.session_status['polling'] = True
        self.listen_backend()

    def listen_backend(self):
        if not self.session_status['polling']:
            return

        polling_logs = self.backend_service.polling()
        for log in polling_logs:
            self.write(log)
        self.after(400, self.listen_backend)

    def service_stop(self):
        self.session_status['polling'] = False

    def show_hint(self):
        msg = f'Required columns: {self.DESTINATION}, {self.PORT}, {self.PACKAGES}, {self.COOLDOWN}, {self.PROTOCOL}'
        showinfo(title="CSV format hint", message=msg)

    def select_file(self):
        filetypes = (('csv files', '*.csv'), ('txt files', '*.txt'))
        filename = filedialog.askopenfilename(title='Open a file', initialdir='~', filetypes=filetypes)

        self.session_status['filename'] = filename
        self.output.insert(INSERT, f"Selected file: {filename.split('/')[-1]}\n")

        if not filename:
            return

        logs = self.backend_service.register_senders(self.session_status['filename'])
        for log in logs:
            self.write(log)

    def clear_journal(self):
        self.output.delete(1.0, END)

    def write(self, msg: str):
        self.output.insert(INSERT, msg)
