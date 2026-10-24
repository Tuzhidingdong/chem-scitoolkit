"""Battery charge/discharge cycling, differential capacity (dQ/dV), and rate capability analysis."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, Optional, Tuple, Dict, Any
from my_sci_toolkit.core.signal import smooth_spectrum
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


@tool(
    name="plot_charge_discharge",
    description="Plot battery galvanostatic charge/discharge curves (Voltage vs Specific Capacity).",
    tags=["electrochem", "battery"]
)
def plot_charge_discharge(
    capacity_mah_g: Sequence[float],
    voltage_v: Sequence[float],
    cycle_index: int = 1,
    c_rate: Optional[str] = "0.1C",
    title: Optional[str] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot battery voltage profile vs specific capacity."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.80)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    ax.plot(capacity_mah_g, voltage_v, color=PALETTES["nature"][0], linewidth=1.2, label=f"Cycle {cycle_index} ({c_rate})")
    ax.set_xlabel(r"Specific Capacity (mAh g$^{-1}$)")
    ax.set_ylabel("Voltage (V vs. Li/Li$^+$)")
    ax.legend()
    if title:
        ax.set_title(title)

    if save_path:
        save_publication_figure(fig, save_path)
    return fig


@tool(
    name="calculate_dqdv",
    description="Compute differential capacity dQ/dV curve from voltage and capacity vectors with noise smoothing.",
    tags=["electrochem", "battery"]
)
def calculate_dqdv(
    voltage: Sequence[float],
    capacity: Sequence[float],
    smooth_window: int = 15,
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate differential capacity dQ/dV (mAh g^-1 V^-1) with Savitzky-Golay filtering."""
    v = np.asarray(voltage, dtype=float)
    q = np.asarray(capacity, dtype=float)

    # Sort monotonically with voltage
    idx_sort = np.argsort(v)
    v_s, q_s = v[idx_sort], q[idx_sort]

    # Smooth raw capacity
    q_smooth = smooth_spectrum(q_s, window_length=smooth_window)
    dq = np.gradient(q_smooth)
    dv = np.gradient(v_s)

    # Avoid zero division
    dv_safe = np.where(np.abs(dv) < 1e-6, 1e-6, dv)
    dqdv = np.abs(dq / dv_safe)

    return v_s, dqdv


@tool(
    name="plot_cycling_stability",
    description="Plot battery cycling life stability showing discharge capacity retention and Coulombic Efficiency over cycles.",
    tags=["electrochem", "battery"]
)
def plot_cycling_stability(
    cycles: Sequence[int],
    discharge_capacity: Sequence[float],
    coulombic_efficiency: Optional[Sequence[float]] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot dual-axis battery cycling stability curve."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.75)
    fig, ax1 = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    c1 = PALETTES["nature"][0]
    ax1.scatter(cycles, discharge_capacity, color=c1, s=12, label="Discharge Capacity")
    ax1.set_xlabel("Cycle Number")
    ax1.set_ylabel(r"Capacity (mAh g$^{-1}$)", color=c1)
    ax1.tick_params(axis='y', labelcolor=c1)

    if coulombic_efficiency is not None:
        ax2 = ax1.twinx()
        c2 = PALETTES["nature"][1]
        ax2.scatter(cycles, coulombic_efficiency, color=c2, s=8, marker='^', label="Coulombic Efficiency")
        ax2.set_ylabel("Coulombic Efficiency (%)", color=c2)
        ax2.tick_params(axis='y', labelcolor=c2)
        ax2.set_ylim(80, 105)

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
