"""Image collage assembly and transparency processing."""

from pathlib import Path
from typing import List, Sequence, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from my_sci_toolkit.io.export import save_publication_figure


def create_panel_collage(
    image_paths: Sequence[str | Path],
    rows: int,
    cols: int,
    labels: Optional[Sequence[str]] = None,
    save_path: Optional[str | Path] = None,
    figsize: Optional[Tuple[float, float]] = None,
) -> Figure:
    """Combine multiple image figures into a publication subfigure panel (e.g. a, b, c, d)."""
    n_images = len(image_paths)
    if rows * cols < n_images:
        raise ValueError(f"Grid {rows}x{cols} too small for {n_images} images.")

    fig, axes = plt.subplots(rows, cols, figsize=figsize or (7.0, 5.0), constrained_layout=True)
    ax_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for idx, img_p in enumerate(image_paths):
        ax = ax_flat[idx]
        img = mpimg.imread(str(img_p))
        ax.imshow(img)
        ax.axis("off")
        
        lbl = labels[idx] if labels and idx < len(labels) else f"({chr(97 + idx)})"
        ax.text(
            0.02, 0.95, lbl,
            transform=ax.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
            ha="left",
            bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.7)
        )

    # Hide unused subplots
    for idx in range(n_images, len(ax_flat)):
        ax_flat[idx].axis("off")

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
