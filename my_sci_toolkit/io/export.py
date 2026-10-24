"""Scientific figure and artifact export utilities."""

import os
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from my_sci_toolkit.config import GLOBAL_CONFIG


def save_publication_figure(
    fig: Figure,
    file_path: str | Path,
    dpi: Optional[int] = None,
    transparent: Optional[bool] = None,
    format: Optional[str] = None,
) -> Path:
    """Save a matplotlib figure with publication-grade formatting (600 dpi, tight bounds).

    Args:
        fig: Matplotlib Figure instance.
        file_path: Target output path.
        dpi: Resolution (default 600).
        transparent: Whether background is transparent.
        format: Image format (e.g. 'png', 'tiff', 'pdf', 'svg').

    Returns:
        Path: Absolute path of saved figure.
    """
    spec = GLOBAL_CONFIG.figure_spec
    out_p = Path(file_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    use_dpi = dpi or spec.dpi
    use_trans = transparent if transparent is not None else spec.transparent
    use_fmt = format or out_p.suffix.lstrip(".") or spec.save_format

    if not out_p.suffix:
        out_p = out_p.with_suffix(f".{use_fmt}")

    fig.savefig(
        out_p,
        dpi=use_dpi,
        transparent=use_trans,
        bbox_inches="tight",
        format=use_fmt,
    )
    return out_p.resolve()
