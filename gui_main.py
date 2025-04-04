import sys
import asyncio
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from src.trader import run_bot
from src.chart_window import ChartWindow
from src.signal_emitter import notifier
from src.config_manager import load_config
import styles  # styles.py is in the root directory

logging.basicConfig(filename="gui_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BotThread(QThread):
    log_signal = pyqtSignal(str)

    def run(self):
        cfg = load_config()
        account_id = cfg.get("OANDA_ACCOUNT_ID")
        token = cfg.get("OANDA_API_TOKEN")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_bot(account_id, token))
        except Exception as e:
            self.log_signal.emit(f"Bot Error: {e}")
        finally:
            loop.close()

class TradingBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AUTO Trader GUI")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(styles.WINDOW_STYLE)

        self.bot_thread = None
        self.chart_window = None

        self.layout = QVBoxLayout()
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet(styles.LABEL_STYLE)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(styles.LOG_TEXT_STYLE)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_reload = QPushButton("Reload Config")
        self.btn_chart = QPushButton("Show Chart")

        for btn in [self.btn_start, self.btn_stop, self.btn_reload, self.btn_chart]:
            btn.setStyleSheet(styles.BUTTON_STYLE)

        self.btn_start.clicked.connect(self.start_bot)
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_reload.clicked.connect(self.reload_config)
        self.btn_chart.clicked.connect(self.show_chart)

        hlayout = QHBoxLayout()
        for b in [self.btn_start, self.btn_stop, self.btn_reload, self.btn_chart]:
            hlayout.addWidget(b)

        self.layout.addWidget(self.status_label)
        self.layout.addLayout(hlayout)
        self.layout.addWidget(self.log_output)
        self.setLayout(self.layout)

        notifier.signal.connect(self.append_log)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.status_label.setText("Status: Running..."))
        self.timer.start(10000)

    def start_bot(self):
        self.status_label.setText("Status: Running")
        self.bot_thread = BotThread()
        self.bot_thread.log_signal.connect(self.append_log)
        self.bot_thread.start()

    def stop_bot(self):
        self.status_label.setText("Status: Stopped")
        logger.info("Bot manually stopped.")
        self.append_log("Bot manually stopped.")

    def reload_config(self):
        load_config()
        logger.info("Config reloaded.")
        self.append_log("Config reloaded.")

    def show_chart(self):
        cfg = load_config()
        self.chart_window = ChartWindow(cfg["OANDA_ACCOUNT_ID"], cfg["OANDA_API_TOKEN"])
        self.chart_window.show()

    def append_log(self, msg):
        self.log_output.append(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingBotApp()
    window.show()
    sys.exit(app.exec_())