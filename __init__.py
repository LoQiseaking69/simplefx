# Import essential functions and classes from autogecko.py
from .autogecko import (
    fetch_price,    # Function to fetch real-time price
    place_order,    # Function to place orders on OANDA
    run_bot,        # Main function to run the trading bot
    SignalEmitter,  # Signal emitter for PyQt5 notifications
    load_config,    # Load configuration from a JSON file
    calculate_rsi,  # Function to calculate the Relative Strength Index (RSI)
    calculate_ema   # Function to calculate the Exponential Moving Average (EMA)
)

# Import classes from chat_window.py for chart display
from .chart_window import (
    ChartWindow,    # Window for displaying live chart
    AsyncWorker     # Async worker to handle async tasks in UI thread
)

# Define the public API of this package by listing all accessible elements
__all__ = [
    "fetch_price",   # Fetch price from OANDA API
    "place_order",   # Place a trading order
    "run_bot",       # Run the trading bot
    "SignalEmitter", # Signal emitter for message notifications
    "load_config",   # Load configurations
    "calculate_rsi", # RSI calculation for technical analysis
    "calculate_ema", # EMA calculation for technical analysis
    "ChartWindow",   # Window for live chart
    "AsyncWorker"    # Worker class to handle async tasks in UI
]
