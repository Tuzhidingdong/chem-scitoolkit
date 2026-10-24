"""Molecular dynamics trajectory metrics (RDF, MSD, Diffusion)."""

import numpy as np
from typing import Sequence, Tuple
from my_sci_toolkit.registry import tool


@tool(
    name="calculate_diffusion_coefficient",
    description="Calculate self-diffusion coefficient D (10^-9 m^2/s) from Mean Squared Displacement (MSD) curve via Einstein relation.",
    tags=["md", "diffusion"]
)
def calculate_diffusion_coefficient(
    time_ps: Sequence[float],
    msd_angstrom2: Sequence[float],
    dim: int = 3,
    fit_range_fraction: Tuple[float, float] = (0.2, 0.8),
) -> Tuple[float, float]:
    """Calculate diffusion coefficient D from Einstein relation: MSD = 2 * dim * D * t.

    Returns:
        Tuple[float, float]: (D in 10^-9 m^2/s, R^2 of linear regime).
    """
    t = np.asarray(time_ps, dtype=float)
    msd = np.asarray(msd_angstrom2, dtype=float)

    n = len(t)
    start_idx = int(n * fit_range_fraction[0])
    end_idx = int(n * fit_range_fraction[1])

    t_fit = t[start_idx:end_idx]
    msd_fit = msd[start_idx:end_idx]

    # Linear fit: slope = 2 * dim * D
    slope, intercept = np.polyfit(t_fit, msd_fit, 1)
    
    # Unit conversion: Å^2 / ps = 10^-20 m^2 / 10^-12 s = 10^-8 m^2/s = 10 * 10^-9 m^2/s
    d_m2_s = (slope / (2.0 * dim)) * 1e-8
    d_scaled = d_m2_s * 1e9  # in units of 10^-9 m^2 / s

    y_pred = slope * t_fit + intercept
    ss_res = np.sum((msd_fit - y_pred) ** 2)
    ss_tot = np.sum((msd_fit - np.mean(msd_fit)) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0

    return float(d_scaled), float(r2)
