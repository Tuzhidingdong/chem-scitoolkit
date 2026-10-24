"""Tests for kinetics simulations and rate equations."""

import numpy as np
from my_sci_toolkit.kinetics.models import nth_order_decay, arrhenius_equation
from my_sci_toolkit.kinetics.nucleation_growth import simulate_nucleation_growth
from my_sci_toolkit.kinetics.thermodynamics import capillary_pressure


def test_nth_order_decay():
    t = np.array([0.0, 10.0, 20.0])
    c = nth_order_decay(t, k=0.1, n=2.0)
    assert c[0] == 1.0
    assert c[1] < c[0]
    assert c[2] < c[1]


def test_nucleation_growth_simulation():
    times, alphas = simulate_nucleation_growth(rate_constants=[0.02, 0.0, 0.0], duration=100.0)
    assert len(times) == len(alphas)
    assert alphas[0] <= alphas[-1]
    assert np.all(alphas >= 0.0) and np.all(alphas <= 1.0)


def test_capillary_pressure():
    # 5 nm pore with water gamma=0.0728 N/m, contact angle 0 deg -> ~58.24 MPa = 58240 kPa
    p_kpa = capillary_pressure(surface_tension_gamma=0.0728, contact_angle_deg=0.0, pore_diameter_m=5e-9)
    assert p_kpa > 1000.0
