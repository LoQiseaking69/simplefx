from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
import numpy as np
import asyncio
from src.api_handler import fetch_price
from src.indicators import calculate_ema, calculate_rsi
from src.config_manager import load_config

class ChartWindow(QDialog):
    def __init__(self, account_id, token, pair="EUR_USD"):
        super().__init__()
        self.setWindowTitle(f"Live Chart - {pair}")
        self.setGeometry(300, 300, 1000, 600)
        self.pair = pair
        self.account_id = account_id
        self.token = token
        self.prices = []
        self.timestamps = []

        self.label = QLabel("Fetching...", self)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: asyncio.create_task(self.update_chart()))
        self.timer.start(5000)

    async def update_chart(self):
        price = await fetch_price(self.account_id, self.token, self.pair)
        if price:
            self.prices.append(price)
            self.timestamps.append(datetime.now())
            if len(self.prices) > 100:
                self.prices.pop(0)
                self.timestamps.pop(0)

            self.label.setText(f"{self.pair} Price: {price:.5f}")
            self.ax.clear()
            self.ax.plot(self.timestamps, self.prices, label="Price")
            if len(self.prices) >= 20:
                ema = calculate_ema(np.array(self.prices), 20)
                self.ax.axhline(ema, color='cyan', linestyle='--', label="EMA")
            if len(self.prices) >= 15:
                rsi = calculate_rsi(np.array(self.prices), 14)
                self.ax.set_title(f"RSI: {rsi:.2f}")
            self.ax.legend()
            self.fig.autofmt_xdate()
            self.canvas.draw()
        else:
            self.label.setText("Price fetch failed.")
