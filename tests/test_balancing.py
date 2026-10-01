import unittest
from bms.cell import Cell
from bms.pack import Pack
from bms.balancing import Balancer


def make_pack(voltages):
    cells = [Cell(cell_id=i) for i in range(len(voltages))]
    pack = Pack(cells)
    pack.update_all(voltages, [25.0] * len(voltages))
    return pack


class TestBalancer(unittest.TestCase):
    def test_no_candidates_when_balanced(self):
        pack = make_pack([3.70, 3.70, 3.70, 3.70])
        balancer = Balancer(threshold=0.02)
        candidates = balancer.get_candidates(pack)
        self.assertEqual(len(candidates), 0)

    def test_candidates_identified_when_imbalanced(self):
        pack = make_pack([3.70, 3.71, 3.75, 3.72])
        balancer = Balancer(threshold=0.02)
        candidates = balancer.get_candidates(pack)
        candidate_ids = [c.cell_id for c in candidates]
        self.assertIn(2, candidate_ids)

    def test_step_reduces_imbalance_over_time(self):
        pack = make_pack([3.70, 3.70, 3.80, 3.70])
        balancer = Balancer(threshold=0.02, bleed_rate_v_per_s=0.01)
        delta_before = pack.voltage_delta()
        balancer.step(pack, dt_seconds=5)
        delta_after = pack.voltage_delta()
        self.assertLess(delta_after, delta_before)

    def test_is_balancing_reflects_active_state(self):
        pack = make_pack([3.70, 3.80])
        balancer = Balancer(threshold=0.02)
        balancer.step(pack, dt_seconds=1)
        self.assertTrue(balancer.is_balancing())

    def test_not_balancing_when_pack_is_even(self):
        pack = make_pack([3.70, 3.70])
        balancer = Balancer(threshold=0.02)
        balancer.step(pack, dt_seconds=1)
        self.assertFalse(balancer.is_balancing())


if __name__ == "__main__":
    unittest.main()
