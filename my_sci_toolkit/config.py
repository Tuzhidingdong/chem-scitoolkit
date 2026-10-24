"""Configuration and specification models for my_sci_toolkit."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class FigureSpec:
    """Standard publication figure dimensions (e.g. Nature, JACS).
    
    Nature standard column widths:
    - Single column: ~89 mm (3.50 in)
    - Double column: ~183 mm (7.20 in)
    - 1.5 column: ~120 mm (4.72 in)
    """
    single_width: float = 3.50
    double_width: float = 7.20
    one_half_width: float = 4.72
    default_height: float = 2.80
    dpi: int = 600
    font_family: str = "Arial"
    font_size: int = 8
    transparent: bool = True
    save_format: str = "png"


@dataclass
class ToolkitConfig:
    """Global configuration settings for scientific toolkit."""
    figure_spec: FigureSpec = field(default_factory=FigureSpec)
    default_output_dir: Path = field(default_factory=lambda: Path("./outputs"))
    gemini_model: str = "gemini-2.5-flash"
    log_level: str = "INFO"

    def ensure_output_dir(self, custom_path: Optional[str | Path] = None) -> Path:
        """Create and return the target directory safely."""
        out_path = Path(custom_path) if custom_path else self.default_output_dir
        out_path.mkdir(parents=True, exist_ok=True)
        return out_path


GLOBAL_CONFIG = ToolkitConfig()
