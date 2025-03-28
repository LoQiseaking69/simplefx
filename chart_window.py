import asyncio
import numpy as np
import pandas as pd
import mplfinance as mpf
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, QThreadPool, QRunnable
from autogecko import fetch_price  # Import the fetch_price method from autogecko.py
import logging

# Configure Logging
logging.basicConfig(filename="chart_window_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class ChartWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Live Trading Chart")
        self.setGeometry(200, 200, 1000, 600)
        
        # Data Storage
        self.prices = []
        self.timestamps = []
        
        # Timer for Chart Update
        self.timer = QTimer()
        self.timer.timeout.connect(self.trigger_fetch)
        self.timer.start(5000)  # Update every 5 seconds
        
        # Status Label
        self.status_label = QLabel("⏳ Gathering data...", self)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Asyncio Event Loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Thread Pool for Async Execution
        self.thread_pool = QThreadPool()
        
        logging.info("ChartWindow initialized.")

    def trigger_fetch(self):
        """Trigger the asyncio task on a separate thread."""
        self.thread_pool.start(AsyncWorker(self.fetch_and_update))

    async def fetch_and_update(self):
        """Fetch latest price and update chart."""
        try:
            # Fetch price using fetch_price from autogecko.py
            price = await fetch_price()  # Assuming fetch_price returns a float price
            timestamp = datetime.now().isoformat()  # Use current time as timestamp
            if price:
                # Append the new data
                self.prices.append(price)
                self.timestamps.append(datetime.fromisoformat(timestamp))  # Convert timestamp to datetime object
                
                # Limit data to last 50 points for the chart
                if len(self.prices) > 50:
                    self.prices.pop(0)
                    self.timestamps.pop(0)
                
                logging.info(f"Fetched Price: {price:.5f}")
                self.status_label.setText(f"✅ Latest Price: {price:.5f}")
                self.update_chart()
            else:
                logging.warning("⚠️ Failed to fetch price.")
                self.status_label.setText("⚠️ Failed to fetch price.")
        except Exception as e:
            logging.error(f"Error in fetch_and_update: {e}")
            self.status_label.setText("❌ Error fetching price.")

    def update_chart(self):
        """Generate and save chart using mplfinance."""
        if len(self.prices) < 5:
            return

        # Create DataFrame with timestamps as the index
        df = pd.DataFrame({
            'Date': self.timestamps,
            'Close': self.prices
        }).set_index('Date')

        # Calculate technical indicators (e.g., EMA, RSI)
        df['EMA'] = df['Close'].ewm(span=14, adjust=False).mean()
        df['RSI'] = self.calculate_rsi(np.array(self.prices))

        # Plot Configuration
        style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size': 10})
        ap = [
            mpf.make_addplot(df['EMA'], color='cyan', width=1.2),
            mpf.make_addplot(df['RSI'], panel=1, color='orange', ylabel='RSI', width=1)
        ]

        # Save Plot to File
        mpf.plot(df, type='line', addplot=ap, style=style, volume=False,
                 figratio=(16, 9), figsize=(10, 6), savefig='chart.png')
        
        logging.info("Chart updated successfully.")

    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI indicator."""
        if len(prices) < period + 1:
            return np.full(len(prices), 50)
        
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        # Exponential Moving Average of Gains and Losses
        avg_gain = np.convolve(gain, np.ones(period) / period, mode='valid')
        avg_loss = np.convolve(loss, np.ones(period) / period, mode='valid')
        
        # Avoid division by zero
        avg_loss = np.where(avg_loss == 0, 1e-10, avg_loss)
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Pad with 50 for initial periods
        return np.concatenate((np.full(period, 50), rsi))


class AsyncWorker(QRunnable):
    """QRunnable to run coroutine in a separate thread."""
    def __init__(self, coroutine_func):
        super().__init__()
        self.coroutine_func = coroutine_func

    def run(self):
        """Execute the coroutine in the event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.coroutine_func())
        loop.close()