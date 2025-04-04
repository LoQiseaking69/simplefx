import unittest
import numpy as np
from src import indicators

class TestIndicators(unittest.TestCase):
    def test_rsi_length_check(self):
        data = np.random.rand(10)
        self.assertEqual(indicators.calculate_rsi(data, 14), 50)

    def test_ema_mean_on_short_data(self):
        data = [1, 2, 3]
        ema = indicators.calculate_ema(data, 10)
        self.assertAlmostEqual(ema, np.mean(data), places=5)
