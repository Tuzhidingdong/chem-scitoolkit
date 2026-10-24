"""Tests for core mathematical, signal processing, and path routines."""

import numpy as np
from my_sci_toolkit.core.signal import normalize_sum, normalize_minmax, baseline_correct
from my_sci_toolkit.structure.crystal import calculate_d_spacing


def test_normalize():
    arr = [1.0, 2.0, 3.0, 4.0]
    norm_s = normalize_sum(arr)
    assert np.isclose(np.sum(norm_s), 1.0)

    norm_m = normalize_minmax(arr)
    assert np.isclose(np.min(norm_m), 0.0)
    assert np.isclose(np.max(norm_m), 1.0)


def test_baseline_correction():
    x = np.linspace(0, 10, 100)
    signal = 2.0 * x + 5.0  # Linear baseline
    corrected = baseline_correct(signal, degree=1)
    assert np.all(corrected >= 0.0)
    assert np.mean(corrected) < np.mean(signal)


def test_d_spacing_cubic():
    # Silicon a = 5.4307 Å, (111) plane d = a / sqrt(3) ≈ 3.1354 Å
    d = calculate_d_spacing("cubic", a=5.4307, b=5.4307, c=5.4307, h=1, k=1, l=1)
    expected = 5.4307 / np.sqrt(3)
    assert np.isclose(d, expected, atol=1e-3)
