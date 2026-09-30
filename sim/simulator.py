"""
simulator.py

Generates simulated sensor data for the BMS to consume — standing in
for real hardware (ADC readings, current sensor, etc.) during
development and demos.

Includes an NTC thermistor conversion helper (beta equation), since a
real BMS never receives temperature directly — it receives a raw ADC
voltage from a voltage-divider circuit and has to convert it itself.
Modeling that conversion here (rather than in bms/cell.py or
bms/pack.py) keeps those classes hardware-agnostic: Cell just wants a
temperature in °C, and doesn't need to know or care whether that value
came from an NTC thermistor, a DS18B20, or a hand-typed test value.
Only the simulation/sensor layer should know about raw voltages,
thermistor constants, or ADC quirks — if you ever swapped to a
DS18B20, you'd only change this file, not bms/cell.py.
"""

import math
import random
from typing import List, Tuple

from bms.pack import Pack


# --- NTC thermistor conversion (beta equation) ---

def adc_voltage_to_temperature(v_out: float, v_supply: float = 3.3,
                                r_fixed: float = 10_000, r0: float = 10_000,
                                t0_celsius: float = 25.0, beta: float = 3950) -> float:
    """
    Converts a raw ADC voltage reading from an NTC voltage-divider circuit
    into a temperature in °C, using the beta equation.

    Circuit assumed: v_supply -> R_fixed -> [ADC node, v_out] -> NTC -> GND

    v_out: measured voltage at the ADC pin
    v_supply: supply voltage to the divider (e.g., 3.3V)
    r_fixed: the fixed resistor value in the divider, in ohms
    r0: thermistor's resistance at reference temperature t0, in ohms
        (from its datasheet, typically 10k)
    t0_celsius: reference temperature for r0 (usually 25°C)
    beta: thermistor's beta constant, in Kelvin (from datasheet, ~3000-4000K)
    """
    if v_out <= 0 or v_out >= v_supply:
        raise ValueError("v_out must be between 0 and v_supply (exclusive)")

    # Solve the voltage divider for thermistor resistance
    r_ntc = r_fixed * (v_out / (v_supply - v_out))

    # Beta equation: 1/T = 1/T0 + (1/beta) * ln(R/R0)
    t0_kelvin = t0_celsius + 273.15
    inv_t = (1.0 / t0_kelvin) + (1.0 / beta) * math.log(r_ntc / r0)
    t_kelvin = 1.0 / inv_t

    return t_kelvin - 273.15


def temperature_to_adc_voltage(temp_celsius: float, v_supply: float = 3.3,
                                r_fixed: float = 10_000, r0: float = 10_000,
                                t0_celsius: float = 25.0, beta: float = 3950) -> float:
    """
    Inverse of adc_voltage_to_temperature — given a "true" temperature,
    computes what raw ADC voltage the thermistor circuit would produce.
    Useful for generating realistic simulated sensor data (see below).
    """
    t_kelvin = temp_celsius + 273.15
    t0_kelvin = t0_celsius + 273.15

    r_ntc = r0 * math.exp(beta * (1.0 / t_kelvin - 1.0 / t0_kelvin))
    v_out = v_supply * (r_ntc / (r_ntc + r_fixed))
    return v_out


# --- Scenario / sensor-read simulation ---

def simulate_sensor_read(true_voltages: List[float], true_temps: List[float],
                          voltage_noise: float = 0.002, temp_noise: float = 0.3,
                          simulate_adc_roundtrip: bool = True) -> Tuple[List[float], List[float]]:
    """
    Takes "true" underlying cell voltages/temperatures and produces noisy,
    sensor-realistic readings — as if they'd actually come through an ADC
    and (for temperature) an NTC thermistor circuit.

    voltage_noise: std dev of simulated voltage sensor noise, in volts
    temp_noise: std dev of simulated temperature noise, in °C
    simulate_adc_roundtrip: if True, temperatures are pushed through
        temperature_to_adc_voltage() then back through
        adc_voltage_to_temperature(), so noise and quantization effects
        of the real thermistor circuit are reflected, not just a
        clean random offset.
    """
    noisy_voltages = [v + random.gauss(0, voltage_noise) for v in true_voltages]

    noisy_temps = []
    for t in true_temps:
        t_noisy_true = t + random.gauss(0, temp_noise)
        if simulate_adc_roundtrip:
            v_adc = temperature_to_adc_voltage(t_noisy_true)
            t_final = adc_voltage_to_temperature(v_adc)
        else:
            t_final = t_noisy_true
        noisy_temps.append(t_final)

    return noisy_voltages, noisy_temps


def apply_scenario_to_pack(pack: Pack, voltages: List[float], temps: List[float],
                            current: float, with_sensor_noise: bool = True):
    """
    Pushes a scenario's "true" values into the pack, optionally passing
    them through simulate_sensor_read() first to mimic real sensor
    imperfection rather than feeding the pack suspiciously clean numbers.
    """
    if with_sensor_noise:
        voltages, temps = simulate_sensor_read(voltages, temps)

    pack.update_all(voltages, temps)
    pack.update_current(current)
