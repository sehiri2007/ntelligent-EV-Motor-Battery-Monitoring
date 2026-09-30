"""
sim package

Simulation layer: generates realistic (noisy) sensor data and named
test scenarios for exercising the bms package without real hardware.

    from sim import get_scenario, apply_scenario_to_pack, list_scenarios
"""

from sim.simulator import (
    adc_voltage_to_temperature,
    temperature_to_adc_voltage,
    simulate_sensor_read,
    apply_scenario_to_pack,
)
from sim.scenarios import SCENARIOS, get_scenario, list_scenarios

__all__ = [
    "adc_voltage_to_temperature", "temperature_to_adc_voltage",
    "simulate_sensor_read", "apply_scenario_to_pack",
    "SCENARIOS", "get_scenario", "list_scenarios",
]
