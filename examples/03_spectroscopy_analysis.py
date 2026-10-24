"""Example 3: Spectroscopy Baseline Correction and Multi-Peak Deconvolution."""

from pathlib import Path
import numpy as np
from my_sci_toolkit import plot_xrd_pattern, plot_xrd_stack
from my_sci_toolkit.spectro.vibrational import deconvolute_peaks, gaussian

output_dir = Path("./outputs")
output_dir.mkdir(exist_ok=True)

# 1. Synthesize XRD pattern with baseline curvature
two_theta = np.linspace(10, 80, 500)
baseline = 50 + 20 * np.sin(two_theta / 15)
peak1 = 300 * np.exp(-((two_theta - 28.5) ** 2) / 0.5)
peak2 = 450 * np.exp(-((two_theta - 33.1) ** 2) / 0.8)
raw_intensity = baseline + peak1 + peak2 + np.random.normal(0, 5, len(two_theta))

fig_xrd = plot_xrd_pattern(
    two_theta=two_theta,
    intensity=raw_intensity,
    label="FeS/FeS2 Composite",
    baseline_corr=True,
    normalize=True,
    save_path=output_dir / "03_xrd_pattern.png",
)

# 2. Deconvolute overlapping Raman band
x_raman = np.linspace(3500, 3700, 200)
p_a = gaussian(x_raman, 100, 3610, 12)
p_b = gaussian(x_raman, 80, 3640, 15)
y_raman = p_a + p_b + np.random.normal(0, 2, len(x_raman))

fig_peaks = deconvolute_peaks(
    x=x_raman,
    y=y_raman,
    initial_centers=[3610, 3640],
    save_path=output_dir / "03_raman_deconvolution.png",
)
print("Saved spectroscopy plots.")
