"""
state_machine.py

Ties the whole system together: IDLE -> CHARGING -> DISCHARGING -> FAULT/SHUTDOWN.

This is the top-level control loop a real BMS firmware would run every
tick — read sensors, update SoC, check protection, decide the next state.
"""

from enum import Enum
from bms.pack import Pack
from bms.soc import SoCEstimator
from bms.protection import ProtectionSystem
from bms.balancing import Balancer


class SystemState(Enum):
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    FAULT = "fault"
    SHUTDOWN = "shutdown"


class BMSStateMachine:
    def __init__(self, pack: Pack, soc_estimator: SoCEstimator,
                 protection: ProtectionSystem, balancer: Balancer):
        self.pack = pack
        self.soc = soc_estimator
        self.protection = protection
        self.balancer = balancer
        self.state = SystemState.IDLE

    def step(self, dt_seconds: float):
        """
        One control loop tick. Assumes pack sensor data (voltages/temps/
        current) has already been updated via pack.update_all() /
        pack.update_current() before this is called.
        """
        # 1. Update SoC based on current draw
        self.soc.update(self.pack.current, dt_seconds)

        # 2. Run protection checks (debounced fault detection)
        shutdown_needed = self.protection.check(self.pack)

        # 3. Balance cells if not in a fault condition
        if not shutdown_needed:
            self.balancer.step(self.pack, dt_seconds)

        # 4. Decide next state
        self._transition(shutdown_needed)

        return self.state

    def _transition(self, shutdown_needed: bool):
        if shutdown_needed:
            self.state = SystemState.SHUTDOWN if self.state == SystemState.FAULT else SystemState.FAULT
            return

        if self.pack.current > 0.05:
            self.state = SystemState.CHARGING
        elif self.pack.current < -0.05:
            self.state = SystemState.DISCHARGING
        else:
            self.state = SystemState.IDLE

    def reset_fault(self):
        """Manual recovery path — e.g., user presses a reset button after inspecting the pack."""
        self.protection.reset()
        self.state = SystemState.IDLE

    def __repr__(self):
        return (
            f"BMSStateMachine(state={self.state.value}, "
            f"soc={self.soc.get_soc_percent():.1f}%, "
            f"pack={self.pack})"
        )
