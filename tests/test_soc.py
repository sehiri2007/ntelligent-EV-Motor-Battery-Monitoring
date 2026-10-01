import unittest
from bms.soc import SoCEstimator


class TestSoCEstimator(unittest.TestCase):
    def test_initial_soc(self):
        soc = SoCEstimator(capacity_ah=2.5, initial_soc=0.8)
        self.assertAlmostEqual(soc.get_soc(), 0.8, places=3)

    def test_discharge_lowers_soc(self):
        soc = SoCEstimator(capacity_ah=2.5, initial_soc=1.0)
        soc.update(current=-2.5, dt_seconds=3600)  # 1 hour at -2.5A = 2.5Ah drained
        self.assertAlmostEqual(soc.get_soc(), 0.0, places=2)

    def test_charge_raises_soc(self):
        soc = SoCEstimator(capacity_ah=2.5, initial_soc=0.0)
        soc.update(current=2.5, dt_seconds=3600)
        self.assertAlmostEqual(soc.get_soc(), 1.0, places=2)

    def test_soc_clamped_at_zero(self):
        soc = SoCEstimator(capacity_ah=2.5, initial_soc=0.0)
        soc.update(current=-5.0, dt_seconds=3600)  # trying to over-discharge
        self.assertGreaterEqual(soc.get_soc(), 0.0)

    def test_soc_clamped_at_one(self):
        soc = SoCEstimator(capacity_ah=2.5, initial_soc=1.0)
        soc.update(current=5.0, dt_seconds=3600)  # trying to overcharge
        self.assertLessEqual(soc.get_soc(), 1.0)

    def test_reset_recalibrates(self):
        soc = SoCEstimator(capacity_ah=2.5, initial_soc=0.5)
        soc.reset(1.0)
        self.assertAlmostEqual(soc.get_soc(), 1.0, places=3)

    def test_invalid_initial_soc_raises(self):
        with self.assertRaises(ValueError):
            SoCEstimator(capacity_ah=2.5, initial_soc=1.5)


if __name__ == "__main__":
    unittest.main()
