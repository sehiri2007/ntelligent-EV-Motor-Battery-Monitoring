"""
scenarios.py

Named, reusable test scenarios for the BMS — each one a "true" set of
cell voltages/temps/current that represents a realistic situation
(normal operation, imbalance, overvoltage, overtemp, overcurrent).

Kept as plain data (not functions) so scenarios are easy to read, add
to, and reference by name from a demo script or README — e.g.
"run the overvoltage_fault scenario" instead of hand-writing values
every time. simulator.py is what actually turns this data into noisy,
sensor-realistic readings and applies it to a Pack.
"""

SCENARIOS = {
    "normal": {
        "description": "Healthy 4S pack, discharging normally, no imbalance.",
        "voltages": [3.70, 3.71, 3.69, 3.70],
        "temps": [25.0, 25.2, 24.8, 25.1],
        "current": -2.0,
    },

    "imbalance": {
        "description": "Cells drifting apart — a good case for balancing.py.",
        "voltages": [3.70, 3.71, 3.75, 3.72],
        "temps": [25.0, 25.3, 26.0, 25.2],
        "current": -2.0,
    },

    "overvoltage_fault": {
        "description": "One cell pushed past the 4.2V limit — should trip protection.py after debounce.",
        "voltages": [3.70, 3.71, 3.72, 4.25],
        "temps": [25.0, 25.2, 25.1, 30.0],
        "current": 2.5,  # charging — realistic context for overvoltage
    },

    "undervoltage_fault": {
        "description": "One cell dropped below the 2.5V cutoff — deep discharge condition.",
        "voltages": [3.70, 3.71, 2.40, 3.68],
        "temps": [25.0, 25.1, 24.9, 25.0],
        "current": -3.0,
    },

    "overtemp_fault": {
        "description": "One cell running hot — should trip protection.py's temperature check.",
        "voltages": [3.70, 3.71, 3.69, 3.70],
        "temps": [25.0, 25.2, 50.0, 25.1],
        "current": -2.0,
    },

    "overcurrent_fault": {
        "description": "Discharge current exceeds the pack's max_discharge_current limit.",
        "voltages": [3.70, 3.71, 3.69, 3.70],
        "temps": [25.0, 25.2, 24.9, 25.1],
        "current": -12.0,  # exceeds a typical 10A max_discharge_current
    },
}


def get_scenario(name: str) -> dict:
    if name not in SCENARIOS:
        available = ", ".join(SCENARIOS.keys())
        raise ValueError(f"Unknown scenario '{name}'. Available: {available}")
    return SCENARIOS[name]


def list_scenarios() -> list:
    return list(SCENARIOS.keys())
