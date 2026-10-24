"""Interfacial thermodynamics, capillary tension, and nanoscale Gibbs free energy models."""

import numpy as np
from typing import Tuple


def capillary_pressure(
    surface_tension_gamma: float = 0.0728,  # N/m (water at 20°C)
    contact_angle_deg: float = 0.0,
    pore_diameter_m: float = 5e-9,  # 5 nm pore
) -> float:
    """Calculate capillary hydrostatic tension (Kelvin-Laplace equation) in kPa.

    -Delta P_cap = 4 * gamma * cos(theta) / d
    """
    theta_rad = np.radians(contact_angle_deg)
    p_pa = (4.0 * surface_tension_gamma * np.cos(theta_rad)) / pore_diameter_m
    return float(p_pa / 1000.0)  # kPa


def nanoscale_solubility_ratio(
    radius_nm: float,
    surface_energy_J_m2: float = 1.0,
    molar_volume_m3_mol: float = 3.4e-5,
    temperature_k: float = 298.15,
) -> float:
    """Ostwald-Freundlich nanoscale solubility enhancement: C(r) / C_bulk = exp(2 * gamma * Vm / (r * R * T))."""
    R_gas = 8.314462
    r_m = radius_nm * 1e-9
    exponent = (2.0 * surface_energy_J_m2 * molar_volume_m3_mol) / (r_m * R_gas * temperature_k)
    return float(np.exp(exponent))
