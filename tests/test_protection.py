import unittest
from bms.cell import Cell, CellState
from bms.pack import Pack
from bms.protection import ProtectionSystem


def make_pack(voltages, temps, current=0.0, max_discharge=10.0, max_charge=5.0):
    cells = [Cell(cell_id=i) for i in range(len(voltages))]
    pack = Pack(cells, max_charge_current=max_charge, max_discharge_current=max_discharge)
    pack.update_all(voltages, temps)
    pack.update_current(current)
    return pack


class TestProtectionSystem(unittest.TestCase):
    def test_no_shutdown_when_pack_healthy(self):
        pack = make_pack([3.70, 3.71, 3.69, 3.70], [25, 25, 25, 25], current=1.0)
        protection = ProtectionSystem(debounce_count=2)
        self.assertFalse(protection.check(pack))

    def test_fault_not_triggered_on_single_bad_reading(self):
        pack = make_pack([3.70, 4.30, 3.69, 3.70], [25, 25, 25, 25], current=1.0)
        protection = ProtectionSystem(debounce_count=3)
        protection.check(pack)
        self.assertNotEqual(pack.get_cell(1).state, CellState.FAULT)

    def test_fault_triggered_after_debounce_count_reached(self):
        pack = make_pack([3.70, 4.30, 3.69, 3.70], [25, 25, 25, 25], current=1.0)
        protection = ProtectionSystem(debounce_count=2)
        protection.check(pack)
        protection.check(pack)
        self.assertEqual(pack.get_cell(1).state, CellState.FAULT)

    def test_counter_resets_when_reading_goes_back_to_normal(self):
        pack = make_pack([3.70, 4.30, 3.69, 3.70], [25, 25, 25, 25], current=1.0)
        protection = ProtectionSystem(debounce_count=2)
        protection.check(pack)  # 1 bad reading

        pack.update_cell(1, voltage=3.70, temperature=25.0)  # back to normal
        protection.check(pack)

        pack.update_cell(1, voltage=4.30, temperature=25.0)  # bad again
        protection.check(pack)
        # counter should have reset, so this is only the 1st bad reading again
        self.assertNotEqual(pack.get_cell(1).state, CellState.FAULT)

    def test_overcurrent_triggers_shutdown_immediately(self):
        pack = make_pack([3.70, 3.70], [25, 25], current=-15.0, max_discharge=10.0)
        protection = ProtectionSystem(debounce_count=5)
        self.assertTrue(protection.check(pack))

    def test_reset_clears_counters(self):
        pack = make_pack([3.70, 4.30], [25, 25], current=1.0)
        protection = ProtectionSystem(debounce_count=2)
        protection.check(pack)
        protection.reset()
        self.assertEqual(protection._fault_counters, {})
        self.assertFalse(protection.shutdown_triggered)


if __name__ == "__main__":
    unittest.main()
