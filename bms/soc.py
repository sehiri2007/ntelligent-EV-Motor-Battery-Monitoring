"""
soc.py

State of Charge (SoC) estimation using Coulomb counting.

Coulomb counting integrates current over time to track how much charge
has entered/left the pack, relative to its rated capacity.

    SoC(t) = SoC(0) + (integral of current dt) / capacity

This is the simplest reliable SoC method and is a standard starting
point for BMS projects. It drifts over time (no self-correction), which
is a known real-world limitation — worth mentioning in your design notes.
"""


class SoCEstimator:
    def __init__(self, capacity_ah: float, initial_soc: float = 1.0):
        """
        capacity_ah: pack capacity in amp-hours
        initial_soc: starting SoC as a fraction (1.0 = 100%)
        """
        if not (0.0 <= initial_soc <= 1.0):
            raise ValueError("initial_soc must be between 0.0 and 1.0")

        self.capacity_ah = capacity_ah
        self.soc = initial_soc
        self._charge_used_ah = (1.0 - initial_soc) * capacity_ah

    def update(self, current: float, dt_seconds: float):
        """
        Call this every time you get a new current reading.

        current: amps, + = charging, - = discharging
        dt_seconds: time elapsed since the last update
        """
        dt_hours = dt_seconds / 3600.0
        charge_delta_ah = current * dt_hours  # + adds charge, - removes it

        self._charge_used_ah -= charge_delta_ah
        self._charge_used_ah = max(0.0, min(self.capacity_ah, self._charge_used_ah))

        self.soc = 1.0 - (self._charge_used_ah / self.capacity_ah)
        return self.soc

    def get_soc(self) -> float:
        return self.soc

    def get_soc_percent(self) -> float:
        return self.soc * 100.0

    def reset(self, soc: float):
        """Manual re-calibration point (e.g., when a full charge is detected)."""
        if not (0.0 <= soc <= 1.0):
            raise ValueError("soc must be between 0.0 and 1.0")
        self.soc = soc
        self._charge_used_ah = (1.0 - soc) * self.capacity_ah

    def __repr__(self):
        return f"SoCEstimator(soc={self.get_soc_percent():.1f}%)"
