"""Publication-quality styling system for Nature, JACS, and ACS."""

import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple
from my_sci_toolkit.config import GLOBAL_CONFIG, FigureSpec


PALETTES = {
    "nature": ["#C0392B", "#2980B9", "#27AE60", "#F39C12", "#8E44AD", "#2C3E50"],
    "jacs": ["#004488", "#DDAA33", "#BB5566", "#000000", "#44BB99", "#99DDFF"],
    "subtle": ["#E74C3C", "#3498DB", "#2ECC71", "#9B59B6", "#34495E", "#1ABC9C"],
}


def apply_style(
    theme: str = "nature",
    font_family: str = "Arial",
    font_size: int = 8,
) -> None:
    """Set global Matplotlib rcParams conforming to Nature/JACS submission guidelines.

    Args:
        theme: Palette name ("nature", "jacs", "subtle").
        font_family: Default sans-serif typography.
        font_size: Standard base font point size (Nature recommends 6-8 pt).
    """
    rc_params: Dict[str, Any] = {
        "font.family": "sans-serif",
        "font.sans-serif": [font_family, "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": font_size,
        "axes.titlesize": font_size,
        "axes.labelsize": font_size,
        "xtick.labelsize": font_size - 1,
        "ytick.labelsize": font_size - 1,
        "legend.fontsize": font_size - 1,
        "legend.frameon": False,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.2,
        "lines.markersize": 4.0,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "axes.unicode_minus": False,
        "figure.dpi": GLOBAL_CONFIG.figure_spec.dpi,
        "savefig.dpi": GLOBAL_CONFIG.figure_spec.dpi,
        "savefig.transparent": True,
    }
    plt.rcParams.update(rc_params)


def get_figure_dimensions(
    columns: str = "single",
    aspect_ratio: float = 0.80,
) -> Tuple[float, float]:
    """Calculate publication figure width and height in inches.

    Args:
        columns: 'single' (3.5 in), 'double' (7.2 in), or '1.5' (4.72 in).
        aspect_ratio: Height-to-width ratio.

    Returns:
        Tuple[float, float]: (width_inch, height_inch).
    """
    spec = GLOBAL_CONFIG.figure_spec
    if columns == "double":
        w = spec.double_width
    elif columns in ("1.5", "one_half"):
        w = spec.one_half_width
    else:
        w = spec.single_width
    h = w * aspect_ratio
    return (w, h)
