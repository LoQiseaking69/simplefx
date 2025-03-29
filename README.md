# AUTO Trade Program

## Overview
The AUTO Trade Program is a fully functional automated trading bot designed to trade financial instruments using the OANDA API. It integrates technical analysis indicators, including RSI and EMA, with PyQt5 for a professional user interface and `mplfinance` for real-time charting.
___
![img](https://github.com/LoQiseaking69/simplefx/blob/main/IMG_9963.jpeg)
___

## Features
- **Automated Trading:** Implements RSI and EMA indicators for buy/sell signals.
- **OANDA API Integration:** Handles order placement, stop loss, and take profit.
- **Live Charting:** Uses `mplfinance` for real-time price charts with RSI and EMA overlays.
- **Configurable Parameters:** Supports `.json` configuration and dynamic reloading.
- **Robust Logging:** Detailed logs for trading actions and chart updates.

## File Structure
```
├── autogecko.py            # Core trading bot logic
├── chart_window.py         # Live charting module
├── main.py                 # PyQt5 UI and app control
├── styles.py               # UI styling
├── config.json             # Config file for parameters (local; make yourself by copying template below and adjusting)
├── trade_log.txt           # Trading activity logs *(will generate after first run)
├── chart_window_log.txt    # Chart window logs **
├── trading_bot_log.txt     # Main application logs **
├── README.md               # Project documentation
```

## Configuration
All parameters can be adjusted in `config.json`:
```json
{
  "OANDA_API_TOKEN": "YOUR_OANDA_API_TOKEN",
  "OANDA_ACCOUNT_ID": "YOUR_ACCOUNT_ID",
  "TRADE_AMOUNT_UNITS": 1000,
  "TRADE_INTERVAL": 30,
  "SESSION_DURATION": 3600,
  "RSI_PERIOD": 14,
  "EMA_PERIOD": 20,
  "RSI_BUY_THRESHOLD": 30,
  "RSI_SELL_THRESHOLD": 70,
  "STOP_LOSS_PERCENTAGE": 0.02,
  "TAKE_PROFIT_PERCENTAGE": 0.03,
  "PAIRS": ["EUR_USD"]
}
```

## Usage
1. **Setup Environment:**
   - Create a virtual environment and install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
2. **Run the Application:**
   - Launch the main UI:
     ```bash
     python main.py
     ```

## License
This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Author
@LoQiseaking69
