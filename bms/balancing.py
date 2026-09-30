"""
balancing.py

Passive balancing: identifies which cells are sitting above the pack
minimum voltage by more than a threshold, and simulates "bleeding" them
down via a resistor until they're back in line with the rest.

This models passive (resistive) balancing, the simplest and most common
approach in hobbyist/small BMS designs — as opposed to active balancing,
which shuffles charge between cells instead of wasting it as heat.
"""

from typing import List
from bms.pack import Pack
from bms.cell import Cell


class Balancer:
    def __init__(self, threshold: float = 0.02, bleed_rate_v_per_s: float = 0.001):
        """
        threshold: volts above pack minimum before a cell is balanced
        bleed_rate_v_per_s: how fast passive balancing lowers a cell's
                             voltage per second (simulated bleed resistor)
        """
        self.threshold = threshold
        self.bleed_rate_v_per_s = bleed_rate_v_per_s
        self.active_cells: List[int] = []  # cell_ids currently being bled

    def get_candidates(self, pack: Pack) -> List[Cell]:
        return pack.cells_needing_balance(threshold=self.threshold)

    def step(self, pack: Pack, dt_seconds: float):
        """
        Call this once per control loop tick. Simulates bleeding down
        any cell currently above threshold relative to the pack minimum.
        """
        candidates = self.get_candidates(pack)
        self.active_cells = [c.cell_id for c in candidates]

        drop = self.bleed_rate_v_per_s * dt_seconds
        for cell in candidates:
            new_voltage = max(cell.voltage - drop, pack.min_cell_voltage())
            cell.update(new_voltage, cell.temperature)

    def is_balancing(self) -> bool:
        return len(self.active_cells) > 0

    def __repr__(self):
        return f"Balancer(active_cells={self.active_cells}, threshold={self.threshold}V)"
