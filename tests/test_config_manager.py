import unittest
from src import config_manager

class TestConfigManager(unittest.TestCase):
    def test_load_default_on_fail(self):
        config = config_manager.load_config()
        self.assertIn("TRADE_INTERVAL", config)
        self.assertGreater(config["TRADE_INTERVAL"], 0)
