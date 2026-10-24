"""Crystallographic geometry and lattice interplanar spacing calculations."""

import numpy as np
from typing import Tuple
from my_sci_toolkit.registry import tool


@tool(
    name="calculate_d_spacing",
    description="Calculate crystallographic interplanar d-spacing (Angstrom) for (hkl) planes across crystal systems.",
    tags=["structure", "crystallography"]
)
def calculate_d_spacing(
    crystal_system: str,
    a: float,
    b: float,
    c: float,
    h: int,
    k: int,
    l: int,
    alpha_deg: float = 90.0,
    beta_deg: float = 90.0,
    gamma_deg: float = 90.0,
) -> float:
    """Calculate d_hkl spacing (Å) using exact analytical metric tensor equations.

    Supports: 'cubic', 'tetragonal', 'orthorhombic', 'hexagonal', 'monoclinic'.
    """
    sys_lower = crystal_system.lower()
    if sys_lower == "cubic":
        inv_d2 = (h ** 2 + k ** 2 + l ** 2) / (a ** 2)
    elif sys_lower == "tetragonal":
        inv_d2 = (h ** 2 + k ** 2) / (a ** 2) + (l ** 2) / (c ** 2)
    elif sys_lower == "orthorhombic":
        inv_d2 = (h ** 2) / (a ** 2) + (k ** 2) / (b ** 2) + (l ** 2) / (c ** 2)
    elif sys_lower == "hexagonal":
        inv_d2 = (4.0 / 3.0) * (h ** 2 + h * k + k ** 2) / (a ** 2) + (l ** 2) / (c ** 2)
    elif sys_lower == "monoclinic":
        beta_rad = np.radians(beta_deg)
        sin_beta = np.sin(beta_rad)
        cos_beta = np.cos(beta_rad)
        inv_d2 = (1.0 / (sin_beta ** 2)) * (
            (h ** 2) / (a ** 2)
            + (k ** 2 * (sin_beta ** 2)) / (b ** 2)
            + (l ** 2) / (c ** 2)
            - (2.0 * h * l * cos_beta) / (a * c)
        )
    else:
        raise ValueError(f"Unsupported crystal system: {crystal_system}")

    if inv_d2 <= 0:
        return 0.0
    return float(1.0 / np.sqrt(inv_d2))
