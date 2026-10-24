"""Unified curve fitting and regression structures."""

from dataclasses import dataclass
from typing import Dict, Any, Callable, Tuple, Optional
import numpy as np
from scipy.optimize import curve_fit


@dataclass
class FitResult:
    """Standard container for non-linear regression results."""
    params: Dict[str, float]
    stderr: Dict[str, float]
    r_squared: float
    x_fit: np.ndarray
    y_fit: np.ndarray
    model_name: str = ""

    def summary(self) -> str:
        lines = [f"=== Fit Result: {self.model_name or 'Nonlinear Regression'} (R² = {self.r_squared:.4f}) ==="]
        for k, v in self.params.items():
            err = self.stderr.get(k, 0.0)
            lines.append(f"  {k} = {v:.6e} ± {err:.6e}")
        return "\n".join(lines)


def calculate_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate coefficient of determination R²."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return float(1.0 - (ss_res / ss_tot))


def fit_model(
    model_func: Callable,
    x_data: np.ndarray,
    y_data: np.ndarray,
    param_names: Tuple[str, ...],
    p0: Optional[Sequence] = None,
    bounds: Optional[Tuple] = None,
    num_points: int = 300,
    model_name: str = "",
) -> FitResult:
    """Fit a mathematical model function to experimental x, y points.

    Args:
        model_func: Callable of signature f(x, *params).
        x_data: 1D array of independent variable.
        y_data: 1D array of dependent variable.
        param_names: Names corresponding to parameter indices.
        p0: Initial guess.
        bounds: Lower and upper bounds for parameters.
        num_points: Number of points for smooth curve reconstruction.
        model_name: Optional descriptive label.

    Returns:
        FitResult: Standardized fitting results with statistical metrics.
    """
    x = np.asarray(x_data, dtype=float)
    y = np.asarray(y_data, dtype=float)

    kwargs = {}
    if p0 is not None:
        kwargs["p0"] = p0
    if bounds is not None:
        kwargs["bounds"] = bounds

    popt, pcov = curve_fit(model_func, x, y, **kwargs)
    
    perr = np.sqrt(np.diag(pcov)) if pcov is not None and np.all(np.isfinite(pcov)) else np.zeros_like(popt)
    
    y_pred = model_func(x, *popt)
    r2 = calculate_r_squared(y, y_pred)

    x_dense = np.linspace(np.min(x), np.max(x), num_points)
    y_dense = model_func(x_dense, *popt)

    params_dict = {name: float(popt[i]) for i, name in enumerate(param_names)}
    stderr_dict = {name: float(perr[i]) for i, name in enumerate(param_names)}

    return FitResult(
        params=params_dict,
        stderr=stderr_dict,
        r_squared=r2,
        x_fit=x_dense,
        y_fit=y_dense,
        model_name=model_name,
    )
