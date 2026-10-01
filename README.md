# Simple Battery Management System (BMS)

A lightweight, simulated Battery Management System written in Python. It
models a 4S (4 cells in series) Li-ion pack — cell/pack data, State of
Charge estimation, passive cell balancing, fault protection, and a
top-level state machine — all exercised through a configurable
simulation layer instead of real hardware.

Built as a college application project: the goal was a clean,
understandable system that demonstrates real BMS concepts end-to-end,
not a production-grade implementation.

## Features

- **Cell & pack modeling** — per-cell voltage/temperature tracking with
  configurable safe limits, aggregated pack-level readings (total
  voltage, max/min cell voltage, temperature spread)
- **State of Charge (SoC) estimation** — Coulomb counting, with
  clamping and manual recalibration support
- **Passive cell balancing** — identifies cells sitting above the pack
  minimum voltage and simulates bleeding them down over time
- **Protection system** — debounced overvoltage/undervoltage/overtemp/
  undertemp detection per cell, plus immediate overcurrent protection
  at the pack level
- **System state machine** — ties everything together:
  `IDLE → CHARGING / DISCHARGING → FAULT → SHUTDOWN`
- **Sensor simulation** — generates realistic noisy sensor data,
  including an NTC thermistor model (beta equation) that converts
  between temperature and raw ADC voltage, the way a real
  voltage-divider circuit would
- **Named test scenarios** — normal operation, cell imbalance, and
  four fault conditions (overvoltage, undervoltage, overtemp,
  overcurrent), ready to run or extend
- **41 unit tests**, using only Python's built-in `unittest` — no
  dependencies required to run them

## Project structure

```
bms-project/
├── README.md
├── bms/                    # Core BMS logic
│   ├── cell.py             # Single-cell data model + limit checks
│   ├── pack.py              # Pack aggregation (voltage, temp, current)
│   ├── soc.py                # State of Charge estimation (Coulomb counting)
│   ├── balancing.py         # Passive cell balancing
│   ├── protection.py        # Debounced fault detection
│   └── state_machine.py     # Top-level system state machine
│
├── sim/                     # Simulation layer (stands in for real hardware)
│   ├── simulator.py         # NTC thermistor model + noisy sensor generation
│   └── scenarios.py          # Named scenarios (normal, imbalance, faults)
│
├── tests/                    # Unit tests (one file per bms/ module)
│   ├── test_cell.py
│   ├── test_pack.py
│   ├── test_soc.py
│   ├── test_balancing.py
│   ├── test_protection.py
│   └── test_state_machine.py
│
└── examples/
    └── run_demo.py           # Runs every scenario through the full system
```

## Design notes

- **`bms/` is hardware-agnostic.** `Cell` and `Pack` only ever deal in
  plain floats (volts, °C, amps) — they have no idea whether that data
  came from a real sensor, a thermistor circuit, or a hand-typed test
  value. All hardware-specific logic (e.g., converting a raw ADC
  voltage into a temperature) lives in `sim/simulator.py` instead. This
  keeps the core logic easy to unit test and easy to port to real
  hardware later — you'd only need to rewrite the sensor layer, not
  the BMS logic itself.
- **Protection uses debounce, except for overcurrent.** A single noisy
  voltage/temperature reading won't trip a fault — the condition has
  to persist for a few consecutive checks (`debounce_count`). Overcurrent
  is the one exception: it's checked and acted on immediately, since an
  excessive current draw is time-critical in a way a slightly-off
  temperature reading isn't.
- **Why Coulomb counting for SoC.** It's the simplest reliable SoC
  method and a standard starting point for BMS projects. Its known
  limitation is drift over time (no self-correction) — real BMS
  firmware would periodically recalibrate against an OCV (open-circuit
  voltage) curve when the pack reaches a known state (e.g., full
  charge). That recalibration hook exists (`SoCEstimator.reset()`) but
  isn't automated here, to keep the project scoped.
- **Thermal sensing.** Simulated as an NTC thermistor with the beta
  equation, the standard low-cost approach for small BMS designs (as
  opposed to Steinhart-Hart, which is more accurate but unnecessary
  for this scope). `sim/simulator.py` can convert in both directions —
  temperature → ADC voltage (to generate realistic test data) and ADC
  voltage → temperature (what real firmware would do on the way in).

## Running the demo

From the project root:

```bash
python3 examples/run_demo.py
```

This builds a 4S pack and runs it through every named scenario
(`normal`, `imbalance`, `overvoltage_fault`, `undervoltage_fault`,
`overtemp_fault`, `overcurrent_fault`), printing how the pack, SoC, and
system state evolve tick by tick.

## Running the tests

No external dependencies needed:



(Works with `pytest tests/` too, if you have it installed.)

## Example output




Note how ΔV (the voltage spread between cells) shrinks tick by tick —
that's the passive balancer actively bleeding down the high cell.

## Known limitations

- SoC estimation drifts over time since it's pure Coulomb counting with
  no automatic OCV-based recalibration.
- Balancing and protection logic are simulated at the software level;
  real hardware would need actual bleed resistors / MOSFETs and ADC
  drivers behind this logic.
- The pack size (4 cells) and limits (e.g., 4.2V/2.5V per cell) assume
  a generic 18650 Li-ion cell and are easy to reconfigure via
  `CellLimits` and `Pack`'s constructor arguments.

## Possible extensions

- OCV-based SoC recalibration
- State of Health (SoH) tracking (capacity fade over cycles)
- Active balancing (charge shuffling instead of resistive bleed)
- A real hardware backend (e.g., reading an actual ADC over I2C)
  replacing `sim/simulator.py`
