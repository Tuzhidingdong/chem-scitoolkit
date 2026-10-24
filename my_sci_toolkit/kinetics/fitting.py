"""Kinetic parameters estimation and Arrhenius activation energy fitting."""

import numpy as np
from typing import Sequence, Optional, Tuple
from my_sci_toolkit.core.fitting import FitResult, fit_model
from my_sci_toolkit.kinetics.models import nth_order_decay, first_order_decay, arrhenius_equation
from my_sci_toolkit.registry import tool


@tool(
    name="fit_reaction_kinetics",
    description="Fit reaction decay data (time, C/C0) to first-order or nth-order kinetic rate laws.",
    tags=["kinetics", "fitting"]
)
def fit_reaction_kinetics(
    time_series: Sequence[float],
    concentration_ratio: Sequence[float],
    order: Optional[float] = None,
) -> FitResult:
    """Fit kinetic rate constant k and optional reaction order n from experimental time series."""
    t = np.asarray(time_series, dtype=float)
    c = np.asarray(concentration_ratio, dtype=float)

    if order is not None:
        # Fixed reaction order, only optimize rate constant k
        def model_fixed(x, k):
            return nth_order_decay(x, k, order)

        return fit_model(
            model_func=model_fixed,
            x_data=t,
            y_data=c,
            param_names=("k",),
            p0=[0.05],
            bounds=([0.0], [np.inf]),
            model_name=f"Decay Kinetics (order={order})",
        )
    else:
        # Optimize both rate constant k and reaction order n
        def model_free(x, k, n):
            return nth_order_decay(x, k, n)

        return fit_model(
            model_func=model_free,
            x_data=t,
            y_data=c,
            param_names=("k", "n"),
            p0=[0.05, 1.5],
            bounds=([0.0, 0.5], [np.inf, 5.0]),
            model_name="Nth-Order Decay Kinetics",
        )


@tool(
    name="fit_arrhenius_activation_energy",
    description="Calculate activation energy Ea (kJ/mol) and pre-exponential factor A from temperature series and rate constants.",
    tags=["kinetics", "thermodynamics"]
)
def fit_arrhenius_activation_energy(
    temperatures_kelvin: Sequence[float],
    rate_constants: Sequence[float],
) -> FitResult:
    """Perform Arrhenius regression to obtain activation energy Ea (kJ/mol)."""
    T = np.asarray(temperatures_kelvin, dtype=float)
    k = np.asarray(rate_constants, dtype=float)

    return fit_model(
        model_func=arrhenius_equation,
        x_data=T,
        y_data=k,
        param_names=("A", "Ea_kJ_mol"),
        p0=[1e5, 50.0],
        bounds=([0.0, 0.0], [1e15, 500.0]),
        model_name="Arrhenius Activation Energy",
    )
