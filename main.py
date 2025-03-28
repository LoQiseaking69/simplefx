import sys
import asyncio
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from asyncqt import QEventLoop
import logging

# Import from package modules
from autogecko import start_bot, stop_bot, reload_config_if_changed, fetch_price
from chart_window import ChartWindow
from styles import BUTTON_STYLE, WINDOW_STYLE, LABEL_STYLE, LOG_TEXT_STYLE

# Configure Logging
logging.basicConfig(filename="trading_bot_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class BotThread(QThread):
    log_signal = pyqtSignal(str)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(start_bot())
        except Exception as e:
            self.log_signal.emit(f"⚠️ BotThread Error: {e}")
            logging.error(f"BotThread Error: {e}")
        finally:
            loop.close()

class TradingBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ AUTO Trade Program")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(WINDOW_STYLE)
        self.bot_thread = None
        self.chart_window = ChartWindow()

        # Initialize Timers
        self.price_timer = QTimer()
        self.price_timer.timeout.connect(lambda: asyncio.create_task(self.fetch_and_update_price()))
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        
        self.init_ui()
        logging.info("TradingBotApp initialized.")

    def init_ui(self):
        # UI Elements
        self.status_label = QLabel("🔵 Status: Idle", self)
        self.status_label.setStyleSheet(LABEL_STYLE)

        self.start_button = self.create_button("▶️ Engage", self.start_bot)
        self.stop_button = self.create_button("⏹️ Disengage", self.stop_bot, enabled=False)
        self.reload_button = self.create_button("♻️ Reload Config", self.reload_config)
        self.chart_button = self.create_button("📊 Show Chart", self.show_chart)

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(LOG_TEXT_STYLE)

        # Layouts
        button_layout = QHBoxLayout()
        for btn in [self.start_button, self.stop_button, self.reload_button, self.chart_button]:
            button_layout.addWidget(btn)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_output)
        self.setLayout(layout)

        logging.info("UI components initialized.")

    def create_button(self, text, handler, enabled=True):
        """Helper to create styled buttons."""
        btn = QPushButton(text, self)
        btn.setStyleSheet(BUTTON_STYLE)
        btn.setEnabled(enabled)
        btn.clicked.connect(handler)
        return btn

    def start_bot(self):
        """Engage the trading bot."""
        self.status_label.setText("🟢 Status: Running")
        message = "🚀 System Online — Initiating OANDA Trading Sequence..."
        self.log_output.append(self.format_log(message))
        logging.info(message)

        self.bot_thread = BotThread()
        self.bot_thread.log_signal.connect(self.log_message)
        self.bot_thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Start Timers
        self.price_timer.start(5000)  # Fetch price every 5 seconds
        self.status_timer.start(10000)  # Update status every 10 seconds

    def stop_bot(self):
        """Disengage the trading bot."""
        try:
            stop_bot()
            self.status_label.setText("🔴 Status: Disengaged")
            message = "⚡ System Offline — Trading Sequence Terminated."
            self.log_output.append(self.format_log(message))
            logging.info(message)

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

            # Stop Timers
            self.price_timer.stop()
            self.status_timer.stop()
        except Exception as e:
            message = f"⚠️ Error stopping bot: {e}"
            self.log_output.append(self.format_log(message))
            logging.error(message)

    def reload_config(self):
        """Reload configuration settings."""
        try:
            reload_config_if_changed()
            message = "♻️ Configuration Reloaded — System Parameters Updated."
            self.log_output.append(self.format_log(message))
            logging.info(message)
        except Exception as e:
            message = f"⚠️ Error reloading config: {e}"
            self.log_output.append(self.format_log(message))
            logging.error(message)

    async def fetch_and_update_price(self):
        """Fetch the latest price asynchronously and update chart + log."""
        try:
            price = await fetch_price()
            if price:
                # Append data to chart window
                self.chart_window.prices.append(price)
                self.chart_window.timestamps.append(datetime.now())
                
                # Limit to last 50 points
                if len(self.chart_window.prices) > 50:
                    self.chart_window.prices.pop(0)
                    self.chart_window.timestamps.pop(0)

                message = f"💰 Fetched Price: {price:.5f}"
                logging.info(message)
            else:
                message = "⚠️ Failed to fetch price."
                logging.warning(message)

            self.log_output.append(self.format_log(message))
        except Exception as e:
            message = f"⚠️ Exception: {e}"
            self.log_output.append(self.format_log(message))
            logging.error(message)

    def update_status(self):
        """Simulate system status updates."""
        message = "📡 Scanning network... Systems stable."
        self.log_output.append(self.format_log(message))
        logging.info(message)

    def show_chart(self):
        """Display the live trading chart."""
        self.chart_window.show()
        logging.info("Chart window displayed.")

    def log_message(self, message):
        """Handle log messages from bot thread."""
        self.log_output.append(self.format_log(message))
        logging.info(f"BotThread Log: {message}")

    @staticmethod
    def format_log(message):
        """Timestamp each log entry."""
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = TradingBotApp()
    window.show()
    loop.run_forever()
