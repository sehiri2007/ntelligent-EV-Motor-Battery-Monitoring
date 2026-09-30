"""
cell.py

Represents a single battery cell in the pack.
Values are typically written here after being read from sensors
via the microcontroller (e.g., over UART/I2C/CAN).
"""

from enum import Enum


class CellState(Enum):
    NORMAL = "normal"
    OVERVOLTAGE = "overvoltage"
    UNDERVOLTAGE = "undervoltage"
    OVERTEMP = "overtemp"
    UNDERTEMP = "undertemp"
    FAULT = "fault"


class Cell:
    """
    Represents one cell's live data.
    This class only stores and updates data — it does NOT decide
    protection logic itself (that's protection.py's job).
    """

    def __init__(self, cell_id: int, voltage: float = 0.0, temperature: float = 25.0):
        self.cell_id = cell_id
        self.voltage = voltage          # volts
        self.temperature = temperature  # Celsius
        self.state = CellState.NORMAL

    def update(self, voltage: float, temperature: float):
        """
        Called whenever new sensor data comes in from the microcontroller.
        """
        self.voltage = voltage
        self.temperature = temperature

    def set_state(self, state: CellState):
        self.state = state

    def __repr__(self):
        return (
            f"Cell(id={self.cell_id}, "
            f"V={self.voltage:.3f}V, "
            f"T={self.temperature:.1f}°C, "
            f"state={self.state.value})"
        )
