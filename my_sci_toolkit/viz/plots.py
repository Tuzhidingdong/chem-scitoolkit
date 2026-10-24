"""High-level publication plot generators."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, Optional, List, Dict, Any
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


@tool(
    name="plot_completion_time_bar",
    description="Plot publication-quality comparison bar chart of reaction completion times (e.g. 40min capillary vs 26h bulk water oxidation).",
    tags=["viz", "kinetics"]
)
def plot_completion_time_bar(
    systems: Sequence[str] = ("Capillary", "Bulk water", "Air"),
    times_h: Sequence[float] = (40.0 / 60.0, 26.0, 280.0),
    unit_labels: Optional[Sequence[str]] = ("40 min", "26 h", "280 h"),
    y_label: str = "Time for complete oxidation (h)",
    title: Optional[str] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot comparative reaction completion time bars with clean Nature-style backgrounds.

    Refactors and generalizes paper_dehydration.kinetic_three.
    """
    apply_style(theme="nature")
    fig_w, fig_h = get_figure_dimensions(columns="single", aspect_ratio=0.85)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    n = len(systems)
    x_pos = np.arange(n)
    times_arr = np.asarray(times_h, dtype=float)
    max_y = float(np.max(times_arr)) * 1.20 if len(times_arr) > 0 else 1.0

    colors = PALETTES["nature"][:n]
    bg_colors = ["#FDEDEC", "#EBF5FB", "#EAFAF1", "#FEF9E7"][:n]

    # Subtle background block for aesthetic visual alignment
    ax.bar(x_pos, [max_y * 0.95] * n, color=bg_colors, width=0.55, edgecolor="none", zorder=1)

    # Actual quantitative values
    bars = ax.bar(x_pos, times_arr, color=colors, width=0.48, edgecolor="black", linewidth=0.8, zorder=3)

    # Labels atop bars
    labels = unit_labels if unit_labels is not None else [f"{t:.1f} h" for t in times_arr]
    for bar, txt in zip(bars, labels):
        h = bar.get_height()
        ax.annotate(
            txt,
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

    ax.set_xticks(x_pos)
    ax.set_xticklabels(systems, fontweight="bold")
    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title, fontweight="bold")

    # Clean borders for modern high-impact presentation
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False)
    ax.set_ylim(0, max_y)

    if save_path:
        save_publication_figure(fig, save_path)

    return fig


@tool(
    name="plot_decay_curve",
    description="Plot reaction decay kinetic curve C/C0 vs time with experimental points and fitted line.",
    tags=["viz", "kinetics"]
)
def plot_decay_curve(
    t_exp: Sequence[float],
    c_exp: Sequence[float],
    t_fit: Optional[Sequence[float]] = None,
    c_fit: Optional[Sequence[float]] = None,
    y_err: Optional[Sequence[float]] = None,
    rate_constant_k: Optional[float] = None,
    k_unit: str = "h⁻¹",
    label: str = "Reaction",
    x_label: str = "Time (min)",
    y_label: str = r"C / C$_0$",
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot concentration decay curve C/C0 with optional error bars and fit curve."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.75)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    c_primary = PALETTES["nature"][0]
    
    if y_err is not None:
        ax.errorbar(t_exp, c_exp, yerr=y_err, fmt='o', color=c_primary, ecolor='black', elinewidth=0.8, capsize=2, label=f"{label} (Exp)")
    else:
        ax.scatter(t_exp, c_exp, color=c_primary, s=18, label=f"{label} (Exp)", zorder=3)

    if t_fit is not None and c_fit is not None:
        fit_lbl = f"Fit (k = {rate_constant_k:.3f} {k_unit})" if rate_constant_k is not None else "Fit"
        ax.plot(t_fit, c_fit, linestyle="--", color=c_primary, linewidth=1.2, label=fit_lbl, zorder=2)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()

    if save_path:
        save_publication_figure(fig, save_path)
    return fig


@tool(
    name="plot_conversion_alpha",
    description="Plot conversion fraction alpha vs time with experimental points and simulation curves.",
    tags=["viz", "kinetics"]
)
def plot_conversion_alpha(
    t_exp: Sequence[float],
    alpha_exp: Sequence[float],
    simulations: Optional[List[Dict[str, Any]]] = None,
    title: Optional[str] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot reaction extent alpha(t) curves (0 to 1) with nucleation/growth simulations."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.75)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    ax.scatter(t_exp, alpha_exp, facecolors='none', edgecolors='grey', s=20, label="Experimental", zorder=3)

    if simulations:
        colors = PALETTES["nature"]
        for idx, sim in enumerate(simulations):
            color = sim.get("color", colors[idx % len(colors)])
            lbl = sim.get("label", f"Sim {idx+1}")
            ax.plot(sim["t"], sim["alpha"], color=color, linewidth=1.0, label=lbl)

    ax.set_xlabel("Time (min)")
    ax.set_ylabel(r"Reaction Extent ($\alpha$)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend()
    if title:
        ax.set_title(title)

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
