from PyQt5.QtCore import QObject, pyqtSignal

class SignalEmitter(QObject):
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.last_message = ""

    def emit_signal(self, message):
        if message != self.last_message:
            self.signal.emit(message)
            self.last_message = message

notifier = SignalEmitter()
