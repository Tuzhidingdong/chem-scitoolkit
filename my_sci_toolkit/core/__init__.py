"""Core computational and signal processing primitives."""

from my_sci_toolkit.core.signal import (
    normalize_sum,
    normalize_minmax,
    baseline_correct,
    smooth_spectrum,
)
from my_sci_toolkit.core.fitting import (
    FitResult,
    fit_model,
    calculate_r_squared,
)
from my_sci_toolkit.core.paths import (
    resolve_path,
    list_files,
    extract_time_from_stem,
)

__all__ = [
    "normalize_sum",
    "normalize_minmax",
    "baseline_correct",
    "smooth_spectrum",
    "FitResult",
    "fit_model",
    "calculate_r_squared",
    "resolve_path",
    "list_files",
    "extract_time_from_stem",
]
