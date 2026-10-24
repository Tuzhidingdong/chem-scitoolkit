"""Reaction pathway free energy diagram generators (replaces Step_diagram scripts)."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, List, Dict, Optional, Union
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


@tool(
    name="plot_free_energy_profile",
    description="Plot publication step diagram of reaction pathway free energies (e.g. HER, CO2RR, OER intermediate states).",
    tags=["kinetics", "viz"]
)
def plot_free_energy_profile(
    pathways: Dict[str, Sequence[float]],
    step_labels: Optional[Sequence[str]] = None,
    energy_unit: str = "eV",
    title: Optional[str] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot multi-pathway reaction coordinate energy profiles with standard step horizontal bars and connect lines.

    Args:
        pathways: Mapping of pathway label -> energy sequence for intermediates.
        step_labels: Names of reaction intermediates along X coordinate.
        energy_unit: Energy unit string ('eV', 'kcal/mol', 'kJ/mol').
        title: Optional diagram title.
        save_path: Output file path.
    """
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.80)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    colors = PALETTES["nature"]
    half_width = 0.25

    for p_idx, (path_name, energies) in enumerate(pathways.items()):
        e_arr = np.asarray(energies, dtype=float)
        n_steps = len(e_arr)
        color = colors[p_idx % len(colors)]

        for s_idx in range(n_steps):
            x_center = s_idx
            y_val = e_arr[s_idx]
            # Horizontal state plateau
            ax.hlines(
                y=y_val,
                xmin=x_center - half_width,
                xmax=x_center + half_width,
                color=color,
                linewidth=1.8,
                label=path_name if s_idx == 0 else None,
            )

            # Connecting dashed transition segment
            if s_idx < n_steps - 1:
                next_y = e_arr[s_idx + 1]
                ax.plot(
                    [x_center + half_width, (s_idx + 1) - half_width],
                    [y_val, next_y],
                    color=color,
                    linestyle=":",
                    linewidth=1.0,
                    alpha=0.7,
                )

    ax.set_ylabel(f"Free Energy ({energy_unit})")
    if step_labels:
        ax.set_xticks(range(len(step_labels)))
        ax.set_xticklabels(step_labels, rotation=0)
    else:
        ax.set_xlabel("Reaction Coordinate")

    ax.axhline(0, color="grey", linestyle="--", linewidth=0.6, alpha=0.5)
    ax.legend()
    if title:
        ax.set_title(title)

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
