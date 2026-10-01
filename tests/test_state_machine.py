import unittest
from bms.cell import Cell
from bms.pack import Pack
from bms.soc import SoCEstimator
from bms.balancing import Balancer
from bms.protection import ProtectionSystem
from bms.state_machine import BMSStateMachine, SystemState


def make_machine(voltages, temps, current, debounce_count=2):
    cells = [Cell(cell_id=i) for i in range(len(voltages))]
    pack = Pack(cells, max_charge_current=5.0, max_discharge_current=10.0)
    pack.update_all(voltages, temps)
    pack.update_current(current)

    soc = SoCEstimator(capacity_ah=2.5, initial_soc=0.8)
    protection = ProtectionSystem(debounce_count=debounce_count)
    balancer = Balancer()
    return BMSStateMachine(pack, soc, protection, balancer), pack


class TestBMSStateMachine(unittest.TestCase):
    def test_starts_idle(self):
        sm, _ = make_machine([3.70, 3.70], [25, 25], current=0.0)
        self.assertEqual(sm.state, SystemState.IDLE)

    def test_transitions_to_discharging(self):
        sm, _ = make_machine([3.70, 3.70], [25, 25], current=-2.0)
        state = sm.step(dt_seconds=5)
        self.assertEqual(state, SystemState.DISCHARGING)

    def test_transitions_to_charging(self):
        sm, _ = make_machine([3.70, 3.70], [25, 25], current=2.0)
        state = sm.step(dt_seconds=5)
        self.assertEqual(state, SystemState.CHARGING)

    def test_soc_updates_on_step(self):
        sm, _ = make_machine([3.70, 3.70], [25, 25], current=-2.5)
        soc_before = sm.soc.get_soc()
        sm.step(dt_seconds=3600)
        self.assertLess(sm.soc.get_soc(), soc_before)

    def test_fault_then_shutdown_escalation(self):
        sm, _ = make_machine([4.30, 3.70], [25, 25], current=1.0, debounce_count=1)
        state1 = sm.step(dt_seconds=5)
        self.assertEqual(state1, SystemState.FAULT)
        state2 = sm.step(dt_seconds=5)
        self.assertEqual(state2, SystemState.SHUTDOWN)

    def test_reset_fault_returns_to_idle(self):
        sm, _ = make_machine([4.30, 3.70], [25, 25], current=0.0, debounce_count=1)
        sm.step(dt_seconds=5)
        sm.reset_fault()
        self.assertEqual(sm.state, SystemState.IDLE)

    def test_balancer_does_not_run_during_fault(self):
        sm, pack = make_machine([4.30, 3.70], [25, 25], current=1.0, debounce_count=1)
        sm.step(dt_seconds=5)
        self.assertFalse(sm.balancer.is_balancing())


if __name__ == "__main__":
    unittest.main()
