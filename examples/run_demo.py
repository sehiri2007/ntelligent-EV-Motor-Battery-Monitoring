"""
run_demo.py

End-to-end demo of the BMS system: builds a 4S pack, runs it through
every named scenario in sim/scenarios.py, and prints a readable report
of how the pack, SoC, balancing, and protection logic respond.

This is the script to point at in your README as "here's it working" —
run it with:
    python3 examples/run_demo.py
"""

import sys
import os

# Allow running this script directly from the examples/ folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bms import Cell, Pack, SoCEstimator, Balancer, ProtectionSystem, BMSStateMachine
from sim import get_scenario, apply_scenario_to_pack, list_scenarios


def build_system(num_cells: int = 4):
    cells = [Cell(cell_id=i) for i in range(num_cells)]
    pack = Pack(cells, max_charge_current=5.0, max_discharge_current=10.0)
    soc = SoCEstimator(capacity_ah=2.5, initial_soc=0.80)
    protection = ProtectionSystem(debounce_count=2)
    balancer = Balancer(threshold=0.02)
    return BMSStateMachine(pack, soc, protection, balancer)


def run_scenario(name: str, ticks: int = 3, dt_seconds: float = 10.0):
    scenario = get_scenario(name)
    sm = build_system(num_cells=len(scenario["voltages"]))

    print(f"=== Scenario: {name} ===")
    print(f"{scenario['description']}")
    print()

    # Apply the scenario's sensor data once (simulating one sustained
    # condition, e.g. a stuck fault or steady discharge) and step the
    # state machine forward several ticks to show debounce/balancing
    # behavior unfold over time.
    apply_scenario_to_pack(
        sm.pack, scenario["voltages"], scenario["temps"], scenario["current"],
        with_sensor_noise=False,  # deterministic output for a clean demo
    )

    for tick in range(1, ticks + 1):
        state = sm.step(dt_seconds=dt_seconds)
        print(f"  Tick {tick}: state={state.value:<12} "
              f"SoC={sm.soc.get_soc_percent():5.1f}%  "
              f"{sm.pack}")

    print()
    return sm


def main():
    print("BMS Demo — running all scenarios\n")
    print(f"Available scenarios: {', '.join(list_scenarios())}\n")

    for name in list_scenarios():
        run_scenario(name)

    print("Demo complete.")


if __name__ == "__main__":
    main()
