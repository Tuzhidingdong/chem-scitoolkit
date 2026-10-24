"""Example 1: Comparative Kinetics Analysis (Capillary 40min vs Bulk 26h).

Demonstrates publication-grade completion time bar chart and conversion alpha curves.
"""

from pathlib import Path
from my_sci_toolkit import plot_completion_time_bar, plot_conversion_alpha, simulate_nucleation_growth

output_dir = Path("./outputs")
output_dir.mkdir(exist_ok=True)

# 1. Comparative completion time bar chart (Nature style)
fig1 = plot_completion_time_bar(
    systems=["Capillary", "Bulk water", "Air"],
    times_h=[40.0 / 60.0, 26.0, 280.0],
    unit_labels=["40 min", "26 h", "280 h"],
    title="FeS Complete Oxidation Time",
    save_path=output_dir / "01_completion_time_comparison.png",
)
print("Saved:", output_dir / "01_completion_time_comparison.png")

# 2. Coupled nucleation-growth conversion alpha(t) simulations
t_fast, alpha_fast = simulate_nucleation_growth(rate_constants=[0.05, 0.0, 0.0], duration=60.0)
t_slow, alpha_slow = simulate_nucleation_growth(rate_constants=[0.001, 0.0, 0.0], duration=60.0)

fig2 = plot_conversion_alpha(
    t_exp=[0, 10, 20, 30, 40, 50, 60],
    alpha_exp=[0.0, 0.25, 0.58, 0.82, 0.98, 1.0, 1.0],
    simulations=[
        {"t": t_fast, "alpha": alpha_fast, "label": "Capillary (Fast)", "color": "#C0392B"},
        {"t": t_slow, "alpha": alpha_slow, "label": "Bulk (Slow)", "color": "#2980B9"},
    ],
    title="Reaction Progress α(t) Comparison",
    save_path=output_dir / "01_conversion_alpha_comparison.png",
)
print("Saved:", output_dir / "01_conversion_alpha_comparison.png")
