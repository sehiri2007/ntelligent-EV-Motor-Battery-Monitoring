import unittest
from bms.cell import Cell
from bms.pack import Pack


def make_pack(voltages, temps, current=0.0):
    cells = [Cell(cell_id=i) for i in range(len(voltages))]
    pack = Pack(cells, max_charge_current=5.0, max_discharge_current=10.0)
    pack.update_all(voltages, temps)
    pack.update_current(current)
    return pack


class TestPack(unittest.TestCase):
    def test_pack_voltage_is_sum_of_cells(self):
        pack = make_pack([3.70, 3.71, 3.69, 3.70], [25, 25, 25, 25])
        self.assertAlmostEqual(pack.pack_voltage(), 14.80, places=2)

    def test_voltage_delta(self):
        pack = make_pack([3.70, 3.75, 3.69, 3.72], [25, 25, 25, 25])
        self.assertAlmostEqual(pack.voltage_delta(), 0.06, places=2)

    def test_update_all_rejects_mismatched_lengths(self):
        cells = [Cell(cell_id=i) for i in range(4)]
        pack = Pack(cells)
        with self.assertRaises(ValueError):
            pack.update_all([3.7, 3.7], [25, 25, 25, 25])

    def test_get_cell_returns_none_for_missing_id(self):
        pack = make_pack([3.70, 3.71], [25, 25])
        self.assertIsNone(pack.get_cell(99))

    def test_cells_needing_balance(self):
        pack = make_pack([3.70, 3.71, 3.75, 3.72], [25, 25, 25, 25])
        candidates = pack.cells_needing_balance(threshold=0.02)
        candidate_ids = [c.cell_id for c in candidates]
        self.assertIn(2, candidate_ids)   # 3.75 is 0.05V above min
        self.assertNotIn(0, candidate_ids)  # 3.70 is the min itself

    def test_overcurrent_detection_charging(self):
        pack = make_pack([3.70, 3.70], [25, 25], current=6.0)
        self.assertTrue(pack.is_overcurrent())

    def test_overcurrent_detection_discharging(self):
        pack = make_pack([3.70, 3.70], [25, 25], current=-11.0)
        self.assertTrue(pack.is_overcurrent())

    def test_pack_healthy_when_all_cells_within_limits(self):
        pack = make_pack([3.70, 3.71, 3.69, 3.70], [25, 25, 25, 25], current=1.0)
        self.assertTrue(pack.is_pack_healthy())

    def test_pack_unhealthy_when_a_cell_is_out_of_limits(self):
        pack = make_pack([3.70, 4.30, 3.69, 3.70], [25, 25, 25, 25], current=1.0)
        self.assertFalse(pack.is_pack_healthy())


if __name__ == "__main__":
    unittest.main()
