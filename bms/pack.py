"""
pack.py

Represents the full battery pack: a collection of Cells.
Aggregates pack-level voltage, temperature, and holds pack current
(shared across all cells in series).
"""

from typing import List
from bms.cell import Cell, CellState


class Pack:
    def __init__(self, cells: List[Cell]):
        self.cells = cells
        self.current = 0.0  # amps, shared across the series pack (+ = charging, - = discharging)

    # --- Aggregated readings ---

    def pack_voltage(self) -> float:
        """Sum of all cell voltages (series pack)."""
        return sum(cell.voltage for cell in self.cells)

    def max_cell_voltage(self) -> float:
        return max(cell.voltage for cell in self.cells)

    def min_cell_voltage(self) -> float:
        return min(cell.voltage for cell in self.cells)

    def voltage_delta(self) -> float:
        """Useful for balancing.py — imbalance between cells."""
        return self.max_cell_voltage() - self.min_cell_voltage()

    def max_temperature(self) -> float:
        return max(cell.temperature for cell in self.cells)

    def avg_temperature(self) -> float:
        return sum(cell.temperature for cell in self.cells) / len(self.cells)

    # --- Updates from microcontroller/sensor data ---

    def update_current(self, current: float):
        self.current = current

    def update_cell(self, cell_id: int, voltage: float, temperature: float):
        for cell in self.cells:
            if cell.cell_id == cell_id:
                cell.update(voltage, temperature)
                return
        raise ValueError(f"No cell with id {cell_id} found in pack")

    # --- Status helpers ---

    def has_fault(self) -> bool:
        return any(cell.state == CellState.FAULT for cell in self.cells)

    def __repr__(self):
        return (
            f"Pack(cells={len(self.cells)}, "
            f"V={self.pack_voltage():.2f}V, "
            f"ΔV={self.voltage_delta():.3f}V, "
            f"Tmax={self.max_temperature():.1f}°C, "
            f"I={self.current:.2f}A)"
        )
