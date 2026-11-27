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



def apply_figure_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Apply an explicit figure profile; legacy plotting defaults remain unchanged until called."""
    from cycler import cycler

    allowed = {
        "background", "width_in", "height_in", "font_family", "font_size",
        "axis_line_width", "line_width", "tick_direction", "tick_size",
        "palette", "dpi", "panel_label_size",
    }
    unknown = set(profile) - allowed
    if unknown:
        raise ValueError(f"unknown figure profile keys: {sorted(unknown)}")
    background = profile.get("background", "white")
    if background not in {"white", "transparent"}:
        raise ValueError("background must be white or transparent")
    dpi = int(profile.get("dpi", 600))
    font_size = float(profile.get("font_size", 8))
    if dpi < 1 or font_size <= 0:
        raise ValueError("dpi and font_size must be positive")
    width = profile.get("width_in")
    height = profile.get("height_in")
    if (width is None) != (height is None):
        raise ValueError("width_in and height_in must be configured together")
    if width is not None and (float(width) <= 0 or float(height) <= 0):
        raise ValueError("figure dimensions must be positive")
    direction = profile.get("tick_direction", "in")
    if direction not in {"in", "out", "inout"}:
        raise ValueError("tick_direction must be in, out or inout")
    palette = profile.get("palette", "nature")
    if isinstance(palette, str):
        if palette not in PALETTES:
            raise ValueError(f"unknown palette: {palette}")
        colors = PALETTES[palette]
    else:
        colors = list(palette)
        if not colors or not all(isinstance(item, str) for item in colors):
            raise ValueError("palette must be a known name or a non-empty color list")
    line_width = float(profile.get("line_width", 1.0))
    axis_width = float(profile.get("axis_line_width", 0.8))
    tick_size = float(profile.get("tick_size", 3.0))
    if min(line_width, axis_width, tick_size) < 0:
        raise ValueError("line, axis and tick widths must be non-negative")
    transparent = background == "transparent"
    plt.rcParams.update({
        "font.family": profile.get("font_family", "Arial"),
        "font.size": font_size,
        "axes.labelsize": font_size,
        "axes.titlesize": font_size,
        "xtick.labelsize": max(1, font_size - 1),
        "ytick.labelsize": max(1, font_size - 1),
        "axes.linewidth": axis_width,
        "lines.linewidth": line_width,
        "xtick.direction": direction,
        "ytick.direction": direction,
        "xtick.major.size": tick_size,
        "ytick.major.size": tick_size,
        "axes.prop_cycle": cycler(color=colors),
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": transparent,
    })
    return dict(profile)


def add_panel_label(ax, label: str, profile: Dict[str, Any] | None = None):
    """Add a consistent panel label using an explicit profile's panel-label size."""
    config = profile or {}
    return ax.text(
        0.02, 0.98, str(label), transform=ax.transAxes,
        ha="left", va="top",
        fontsize=float(config.get("panel_label_size", config.get("font_size", 8))),
        fontweight="bold",
    )


def save_figure_profiled(fig, output_path, profile: Dict[str, Any], *, metadata: Dict[str, str] | None = None):
    """Export a figure with explicit size, DPI, background and a supported raster/vector format."""
    from pathlib import Path

    apply_figure_profile(profile)
    width = profile.get("width_in")
    height = profile.get("height_in")
    if width is not None and height is not None:
        fig.set_size_inches(float(width), float(height), forward=True)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    extension = target.suffix.lower().lstrip(".")
    supported = {"png", "tif", "tiff", "pdf", "svg", "eps"}
    if extension not in supported:
        raise ValueError(f"unsupported figure export format: {extension}")
    kwargs = {
        "dpi": int(profile.get("dpi", 600)),
        "transparent": profile.get("background", "white") == "transparent",
        "format": extension,
    }
    if metadata and extension in {"png", "pdf", "svg"}:
        kwargs["metadata"] = metadata
    fig.savefig(target, **kwargs)
    return target
