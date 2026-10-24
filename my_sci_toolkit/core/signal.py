"""Signal processing algorithms for scientific spectra and data series."""

import numpy as np
from typing import Union, Sequence
from scipy.signal import savgol_filter


def normalize_sum(arr: Sequence[float]) -> np.ndarray:
    """Normalize array values so that their sum equals 1.0.

    Args:
        arr: Sequence of numeric values.

    Returns:
        np.ndarray: Normalized 1D numpy array.
    """
    data = np.asarray(arr, dtype=float)
    total = np.sum(data)
    if total == 0:
        return data.copy()
    return data / total


def normalize_minmax(arr: Sequence[float]) -> np.ndarray:
    """Normalize array values to standard range [0.0, 1.0].

    Args:
        arr: Sequence of numeric values.

    Returns:
        np.ndarray: Normalized 1D numpy array.
    """
    data = np.asarray(arr, dtype=float)
    d_min = np.min(data)
    d_max = np.max(data)
    if d_max == d_min:
        return np.zeros_like(data)
    return (data - d_min) / (d_max - d_min)


def baseline_correct(
    intensity: Sequence[float],
    method: str = "modpoly",
    degree: int = 2,
    max_iter: int = 50,
    tol: float = 1e-4,
) -> np.ndarray:
    """Perform baseline removal via modified polynomial fitting (pure numpy implementation).

    Replaces redundant external dependencies like BaselineRemoval with native vectorized code.

    Args:
        intensity: 1D array of spectral intensity.
        method: Method name, currently 'modpoly'.
        degree: Degree of polynomial baseline.
        max_iter: Maximum iterations for baseline threshold convergence.
        tol: Convergence tolerance.

    Returns:
        np.ndarray: Baseline-corrected intensity values.
    """
    y = np.asarray(intensity, dtype=float)
    n = len(y)
    x = np.linspace(-1, 1, n)
    
    # Modified polynomial baseline correction algorithm (Lieber & Mahadevan-Jansen, 2003)
    coeffs = np.polyfit(x, y, degree)
    base = np.polyval(coeffs, x)
    
    for _ in range(max_iter):
        y_mod = np.minimum(y, base)
        new_coeffs = np.polyfit(x, y_mod, degree)
        new_base = np.polyval(new_coeffs, x)
        if np.max(np.abs(new_base - base)) < tol:
            break
        base = new_base
        
    corrected = y - base
    return np.maximum(corrected, 0.0)


def smooth_spectrum(
    y: Sequence[float],
    window_length: int = 9,
    polyorder: int = 3,
) -> np.ndarray:
    """Apply Savitzky-Golay smoothing to eliminate high-frequency experimental noise.

    Args:
        y: Signal array.
        window_length: Filter window size (must be odd).
        polyorder: Polynomial order for filter fit.

    Returns:
        np.ndarray: Smoothed signal.
    """
    data = np.asarray(y, dtype=float)
    if len(data) <= window_length:
        return data.copy()
    if window_length % 2 == 0:
        window_length += 1
    return savgol_filter(data, window_length, polyorder)
