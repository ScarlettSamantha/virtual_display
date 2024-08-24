import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class ConsoleLogger(logging.Handler):
    def __init__(self, console_text: ScrolledText) -> None:
        super().__init__()
        self.console_text = console_text

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.console_text.configure(state="normal")
        self.console_text.insert(tk.END, msg + "\n")
        self.console_text.configure(state="disabled")
        self.console_text.yview(tk.END)


def setup_logging(console_text: ScrolledText) -> None:
    handler = ConsoleLogger(console_text)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
