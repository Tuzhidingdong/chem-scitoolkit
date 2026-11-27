"""Visualization module for publication-grade scientific graphics."""

from my_sci_toolkit.viz.style import (
    apply_style, get_figure_dimensions, PALETTES,
    apply_figure_profile, add_panel_label, save_figure_profiled,
)
from my_sci_toolkit.viz.plots import (
    plot_completion_time_bar,
    plot_decay_curve,
    plot_conversion_alpha,
)
from my_sci_toolkit.viz.collage import create_panel_collage

__all__ = [
    "apply_style",
    "apply_figure_profile",
    "add_panel_label",
    "save_figure_profiled",
    "get_figure_dimensions",
    "PALETTES",
    "plot_completion_time_bar",
    "plot_decay_curve",
    "plot_conversion_alpha",
    "create_panel_collage",
]
