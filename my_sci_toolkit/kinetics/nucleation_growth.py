"""Coupled nucleation-growth differential simulation (generalizes original 'sovleers' and induction methods)."""

import numpy as np
from typing import Sequence, Tuple, List, Dict, Any
from my_sci_toolkit.registry import tool


@tool(
    name="simulate_nucleation_growth",
    description="Simulate solid-state phase transformation progress alpha(t) from nucleation and growth rate constants.",
    tags=["kinetics", "simulation"]
)
def simulate_nucleation_growth(
    rate_constants: Sequence[float] = (0.015, 0.0, 0.0),
    duration: float = 600.0,
    dt: float = 1.0,
    alpha_init: float = 0.01,
    induction_time: float = 0.0,
    k_induction: float = 0.001,
) -> Tuple[np.ndarray, np.ndarray]:
    """Solve the coupled solid-state nucleation and growth rate equation.

    d_alpha / dt = 5 * (1 - alpha)^(3/2) * k_n + 25 * (1 - alpha)^(3/2) * alpha^(3/2) * k_gt + alpha^2 * k_ga

    Args:
        rate_constants: Tuple of [k_nucleation, k_grain_growth, k_aggregation].
        duration: Total reaction simulation time (min).
        dt: Simulation time step (min).
        alpha_init: Starting boundary fraction.
        induction_time: Initial induction plateau delay (min).
        k_induction: Induction rate slope.

    Returns:
        Tuple[np.ndarray, np.ndarray]: (time_array, alpha_array).
    """
    times: List[float] = []
    alphas: List[float] = []

    k_n = rate_constants[0] if len(rate_constants) > 0 else 0.0
    k_gt = rate_constants[1] if len(rate_constants) > 1 else 0.0
    k_ga = rate_constants[2] if len(rate_constants) > 2 else 0.0

    t = 0.0
    alpha = alpha_init

    # Induction phase
    if induction_time > 0:
        while t < induction_time:
            times.append(t)
            alphas.append(min(t * k_induction, alpha_init))
            t += dt

    # Transformation phase
    while t <= duration:
        times.append(t)
        alphas.append(min(alpha, 1.0))

        # Core non-linear rate term
        rate = (
            5.0 * ((max(1.0 - alpha, 0.0)) ** 1.5) * k_n
            + 25.0 * ((max(1.0 - alpha, 0.0)) ** 1.5) * ((max(alpha, 0.0)) ** 1.5) * k_gt
            + (alpha ** 2.0) * k_ga
        )
        alpha += rate * dt
        t += dt
        if alpha >= 1.0:
            break

    return np.asarray(times, dtype=float), np.asarray(alphas, dtype=float)
