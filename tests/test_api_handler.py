import unittest
from src import api_handler

class TestAPIHandler(unittest.TestCase):
    def test_fetch_price_invalid_token(self):
        result = api_handler.fetch_price("INVALID", "XXX", "EUR_USD")
        self.assertIsNone(result)
