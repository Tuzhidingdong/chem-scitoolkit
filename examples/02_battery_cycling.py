"""Example 2: Battery Galvanostatic Cycling and dQ/dV Differential Capacity."""

from pathlib import Path
import numpy as np
from my_sci_toolkit import plot_charge_discharge, calculate_dqdv
from my_sci_toolkit.electrochem.cycling import plot_cycling_stability

output_dir = Path("./outputs")
output_dir.mkdir(exist_ok=True)

# Generate synthetic voltage and capacity profiles
q = np.linspace(0, 180, 200)
v = 3.0 + 1.2 / (1.0 + np.exp(-(q - 90) / 15)) + np.random.normal(0, 0.002, len(q))

# 1. Voltage vs Capacity
fig_cd = plot_charge_discharge(
    capacity_mah_g=q,
    voltage_v=v,
    cycle_index=1,
    c_rate="0.1C",
    save_path=output_dir / "02_battery_voltage_curve.png",
)

# 2. Differential capacity dQ/dV
v_sort, dqdv = calculate_dqdv(v, q, smooth_window=11)
print(f"Computed dQ/dV points: {len(dqdv)}, peak voltage at: {v_sort[np.argmax(dqdv)]:.3f} V")

# 3. Cycling life retention
cycles = list(range(1, 101))
retention = [180.0 * (0.999 ** c) + np.random.normal(0, 0.5) for c in cycles]
coulombic_eff = [99.2 + np.random.normal(0, 0.2) for _ in cycles]

fig_cycle = plot_cycling_stability(
    cycles=cycles,
    discharge_capacity=retention,
    coulombic_efficiency=coulombic_eff,
    save_path=output_dir / "02_battery_cycling_stability.png",
)
print("Saved battery analysis plots.")
