"""
protection.py

Safety layer: watches the pack for out-of-limits conditions
(overvoltage, undervoltage, overtemp, undertemp, overcurrent) and
decides when a real fault should be declared.

Design note: individual Cells flag themselves as e.g. OVERVOLTAGE the
instant a single bad reading comes in (see cell.py's _refresh_state).
But real BMS firmware doesn't trip on one noisy reading — it debounces,
requiring the condition to persist for N consecutive checks before
declaring a fault and calling for shutdown. That debounce logic lives
here, not in Cell.
"""

from bms.pack import Pack
from bms.cell import CellState


class ProtectionSystem:
    def __init__(self, debounce_count: int = 3):
        """
        debounce_count: number of consecutive bad readings required
                        before a fault is declared for a given cell.
        """
        self.debounce_count = debounce_count
        self._fault_counters = {}  # cell_id -> consecutive bad-reading count
        self.shutdown_triggered = False

    def check(self, pack: Pack) -> bool:
        """
        Call this once per control loop tick, after sensor data has been
        updated. Returns True if a shutdown should be triggered.
        """
        for cell in pack.cells:
            bad_reading = cell.state in (
                CellState.OVERVOLTAGE,
                CellState.UNDERVOLTAGE,
                CellState.OVERTEMP,
                CellState.UNDERTEMP,
            )

            if bad_reading:
                self._fault_counters[cell.cell_id] = self._fault_counters.get(cell.cell_id, 0) + 1
            else:
                self._fault_counters[cell.cell_id] = 0

            if self._fault_counters[cell.cell_id] >= self.debounce_count:
                cell.set_fault()

        overcurrent_fault = pack.is_overcurrent()

        self.shutdown_triggered = pack.has_fault() or overcurrent_fault
        return self.shutdown_triggered

    def reset(self):
        """Clear fault counters (e.g., after a manual fault-reset button press)."""
        self._fault_counters = {}
        self.shutdown_triggered = False

    def __repr__(self):
        return f"ProtectionSystem(shutdown_triggered={self.shutdown_triggered})"
