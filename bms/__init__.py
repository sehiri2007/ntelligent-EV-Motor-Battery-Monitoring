"""
bms package

Core battery management system logic: cell/pack data models,
SoC estimation, balancing, protection, and the system state machine.

This file defines what's available when someone does:
    from bms import Cell, Pack

instead of having to know the internal file layout
(bms.cell.Cell, bms.pack.Pack, etc.).
"""

from bms.cell import Cell, CellState, CellLimits
from bms.pack import Pack
from bms.soc import SoCEstimator
from bms.balancing import Balancer
from bms.protection import ProtectionSystem
from bms.state_machine import BMSStateMachine, SystemState

__all__ = [
    "Cell",
    "CellState",
    "CellLimits",
    "Pack",
    "SoCEstimator",
    "Balancer",
    "ProtectionSystem",
    "BMSStateMachine",
    "SystemState",
]

__version__ = "0.1.0"
