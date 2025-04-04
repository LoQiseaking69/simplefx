#Automated OANDA Trading Bot

## Overview
`A production-grade automated trading bot built for the OANDA platform. It leverages RSI and EMA technical indicators to make informed trade decisions and features a PyQt5 GUI, real-time charting with `mplfinance`, modular architecture, CLI control, and a scheduler.

___
![img](https://github.com/LoQiseaking69/simplefx/blob/main/IMG_9963.jpeg)
___

## Features
- **Automated Trading Logic:** Implements RSI/EMA strategies with stop-loss and take-profit mechanisms.
- **Modular Design:** Clean separation of API access, indicators, config management, and UI.
- **CLI Interface:** Control bot sessions directly via `main.py` with command-line arguments.
- **PyQt5 GUI:** Professional UI for manual control and status monitoring.
- **Live Charting:** Real-time visualization with `mplfinance`, including RSI and EMA overlays.
- **Dynamic Config Reload:** Load or override config from `config.json` or environment.
- **Resilient API Layer:** Retries, backoff, and error handling built-in.
- **Logging:** Detailed logging for trading, charting, and system diagnostics.
- **Test Scaffolds:** Unit tests for core logic included under `/tests`.

## File Structure
```
simplefx/
├── main.py                    # CLI entry point for trading bot
├── gui_main.py                # PyQt5 application launcher
├── scheduler.py               # Time-based session controller
├── src/
│   ├── api_handler.py         # OANDA API interactions
│   ├── indicators.py          # RSI and EMA calculations
│   ├── config_manager.py      # Config loader with defaults
│   ├── signal_emitter.py      # Signal emission and broadcasting
│   ├── trader.py              # Core trading logic
│   └── chart_window.py        # Live mplfinance chart window
├── tests/
│   ├── test_api_handler.py    # Basic test for API handler
│   ├── test_indicators.py     # Test for RSI/EMA calculation
│   └── test_config_manager.py # Config loading test
├── config.json                # Editable config file
├── trade_log.txt              # Generated trading log
├── README.md                  # Project documentation
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
1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the CLI:**
```bash
python main.py --start
```

3. **Optional CLI Flags:**
```bash
--status   # Display loaded config
--reload   # Reload configuration
```

## License
This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
