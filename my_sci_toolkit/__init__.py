"""my_sci_toolkit: A Modern Scientific Computing & Visualization Toolkit.

Integrated modules:
- core: Mathematical, signal normalization, baseline correction, and robust path operations.
- io: Tabular data ingestion and structure format conversion.
- kinetics: Reaction rate laws, Arrhenius analysis, nucleation-growth simulations, and energy diagrams.
- electrochem: Battery charge/discharge, differential capacity dQ/dV, and impedance analysis.
- spectro: High-impact XRD, FTIR, Raman, XPS, and EPR spectrum processing.
- viz: Publication-grade styling (Nature, JACS) and composite plotting.
- ai_agent: Natural language interface and tool orchestrator.
"""

from my_sci_toolkit.ai_agent import Agent
from my_sci_toolkit.registry import tool, REGISTRY
from my_sci_toolkit.config import GLOBAL_CONFIG

# High-level convenient exports
from my_sci_toolkit.viz.plots import (
    plot_completion_time_bar,
    plot_decay_curve,
    plot_conversion_alpha,
)
from my_sci_toolkit.kinetics.fitting import (
    fit_reaction_kinetics,
    fit_arrhenius_activation_energy,
)
from my_sci_toolkit.kinetics.nucleation_growth import (
    simulate_nucleation_growth,
)
from my_sci_toolkit.electrochem.cycling import (
    plot_charge_discharge,
    calculate_dqdv,
)
from my_sci_toolkit.spectro.xrd import (
    plot_xrd_pattern,
    plot_xrd_stack,
)

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "tool",
    "REGISTRY",
    "GLOBAL_CONFIG",
    "plot_completion_time_bar",
    "plot_decay_curve",
    "plot_conversion_alpha",
    "fit_reaction_kinetics",
    "fit_arrhenius_activation_energy",
    "simulate_nucleation_growth",
    "plot_charge_discharge",
    "calculate_dqdv",
    "plot_xrd_pattern",
    "plot_xrd_stack",
]
