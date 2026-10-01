import unittest
from bms.cell import Cell, CellState, CellLimits


class TestCell(unittest.TestCase):
    def test_default_state_is_normal(self):
        cell = Cell(cell_id=0, voltage=3.7, temperature=25.0)
        self.assertEqual(cell.state, CellState.NORMAL)
        self.assertTrue(cell.is_healthy())

    def test_overvoltage_detected_on_update(self):
        cell = Cell(cell_id=0)
        cell.update(voltage=4.3, temperature=25.0)
        self.assertEqual(cell.state, CellState.OVERVOLTAGE)
        self.assertFalse(cell.is_healthy())

    def test_undervoltage_detected_on_update(self):
        cell = Cell(cell_id=0)
        cell.update(voltage=2.0, temperature=25.0)
        self.assertEqual(cell.state, CellState.UNDERVOLTAGE)

    def test_overtemp_detected_on_update(self):
        cell = Cell(cell_id=0)
        cell.update(voltage=3.7, temperature=60.0)
        self.assertEqual(cell.state, CellState.OVERTEMP)

    def test_custom_limits_are_respected(self):
        tight_limits = CellLimits(min_voltage=3.0, max_voltage=4.0)
        cell = Cell(cell_id=0, limits=tight_limits)
        cell.update(voltage=4.05, temperature=25.0)
        self.assertEqual(cell.state, CellState.OVERVOLTAGE)

    def test_history_is_capped(self):
        cell = Cell(cell_id=0)
        cell._history_cap = 5
        for i in range(10):
            cell.update(voltage=3.7, temperature=25.0)
        self.assertLessEqual(len(cell.voltage_history), 5)

    def test_set_fault_overrides_state(self):
        cell = Cell(cell_id=0)
        cell.set_fault()
        self.assertEqual(cell.state, CellState.FAULT)


if __name__ == "__main__":
    unittest.main()
