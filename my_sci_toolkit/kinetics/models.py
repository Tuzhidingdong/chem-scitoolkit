"""Kinetic rate laws, decay functions, and transformation equations."""

import numpy as np


def first_order_decay(t: np.ndarray, k: float) -> np.ndarray:
    """First-order decay model: C/C0 = exp(-k * t)."""
    return np.exp(-k * t)


def nth_order_decay(t: np.ndarray, k: float, n: float) -> np.ndarray:
    """Nth-order decay model: C/C0 = (1 + (n - 1) * k * t) ** (-1 / (n - 1)).

    For n = 1, asymptotically returns exp(-k * t).
    """
    if np.isclose(n, 1.0):
        return np.exp(-k * t)
    base = 1.0 + (n - 1.0) * k * t
    base = np.maximum(base, 1e-12)
    return base ** (-1.0 / (n - 1.0))


def avrami_nucleation(t: np.ndarray, k: float, n: float) -> np.ndarray:
    """Johnson-Mehl-Avrami-Kolmogorov (JMAK) phase transformation: alpha = 1 - exp(-k * t^n)."""
    return 1.0 - np.exp(-k * (t ** n))


def pseudo_second_order(t: np.ndarray, k2: float, qe: float) -> np.ndarray:
    """Pseudo-second-order kinetic model for adsorption: q_t = (k2 * qe^2 * t) / (1 + k2 * qe * t)."""
    numerator = k2 * (qe ** 2) * t
    denominator = 1.0 + k2 * qe * t
    return numerator / np.maximum(denominator, 1e-12)


def arrhenius_equation(T_kelvin: np.ndarray, A: float, Ea_kJ_mol: float) -> np.ndarray:
    """Arrhenius equation: k = A * exp(-Ea / (R * T))."""
    R_gas = 8.314462e-3  # kJ / (mol * K)
    return A * np.exp(-Ea_kJ_mol / (R_gas * T_kelvin))
