---
name: chem-scitoolkit
description: "Universal toolkit for computational chemistry, materials science, and Nature/JACS-grade publication graphics. Use this skill when the user asks to process DFT calculations (CP2K, VASP, ORCA), perform Bader/Hirshfeld charge analysis, compute adsorption energies, parse/plot PDOS/DOS/COHP, analyze battery cycling (GCD/dQ/dV/EIS), fit reaction kinetics, deconvolve spectra (XRD/FTIR/Raman/XPS), or generate publication-ready multi-panel scientific figures."
---

# chem-scitoolkit: Computational Chemistry & Publication Graphics Toolkit

`chem-scitoolkit` (`my_sci_toolkit`) is an end-to-end Python toolkit designed for computational chemists, materials scientists, and experimental researchers. It automates simulation input generation, quantum/classical output parsing, spectroscopic deconvolution, battery electrochemistry, and publication-ready visualization (Nature/JACS standard, Arial font, 600 DPI).

---

## When to Activate This Skill

Activate this skill whenever the task involves:
1. **Quantum Chemistry & DFT Workflows**:
   - Setting up or parsing **CP2K**, **VASP**, or **ORCA** calculations.
   - Performing **Bader charge partition**, **Hirshfeld charge extraction**, or topological QTAIM calibrations.
   - Extracting and plotting **PDOS / LPDOS** (projected density of states), **TDOS**, or **COHP/COOP** bonding spectra with Fermi level alignment ($E - E_F = 0$).
   - Calculating adsorption energies ($E_{\text{ads}} = E_{\text{slab+adsorbate}} - E_{\text{slab}} - E_{\text{adsorbate}}$).
2. **Spectroscopic Analysis & Deconvolution**:
   - **XRD**: Pattern plotting, peak matching, Rietveld background subtraction, Scherrer crystallite size calculation.
   - **FTIR & Raman**: Multi-peak fitting (Gaussian, Lorentzian, Voigt), baseline correction (ALS, polynomial), peak area integration.
   - **XPS & EPR**: C 1s charge calibration (284.8 eV), core-level doublet deconvolution, EPR $g$-factor determination.
3. **Electrochemistry & Battery Performance**:
   - Galvanostatic charge/discharge (GCD) profiles, differential capacity curves ($dQ/dV$), Coulombic efficiency, rate capability.
   - Electrochemical Impedance Spectroscopy (EIS) Nyquist/Bode plots and equivalent circuit fitting (Randles).
4. **Reaction Kinetics & Thermodynamics**:
   - Rate constant fitting (0th, 1st, 2nd, Avrami, pseudo-first order, Elovich).
   - Arrhenius activation energy ($E_a$) and Eyring transition state parameters ($\Delta H^\ddagger, \Delta S^\ddagger$).
   - Nucleation and growth kinetics (JMAK model).
   - Reaction energy profiles and free energy landscape visualization.
5. **Publication-Grade Scientific Visualization**:
   - Formatting single or multi-panel figures according to Nature/JACS style standards (`my_sci_toolkit.viz.set_pub_style()`).
   - Assembling subpanels (a, b, c, d...) with clean labels, unified typography (Arial), and high-resolution export (300/600 DPI `.tif`, `.png`, `.pdf`).

---

## Environment & Python Execution

In this workspace, always execute scripts with the project's Anaconda Python environment:
```powershell
& "D:\Software\Anacoda\python.exe" script.py
```

To run unit tests:
```powershell
& "D:\Software\Anacoda\python.exe" -m pytest tests/
```

---

## Core Module Structure

The package is organized under `my_sci_toolkit/`:

```text
my_sci_toolkit/
├── viz/             # Publication styles, plots (bar, decay, alpha, dos), figure collage
├── simulation/      # CP2K, VASP, ORCA, Multiwfn, LAMMPS builders, parsers & Slurm
├── spectro/         # XRD, FTIR, Raman, XPS, and EPR spectrum analysis
├── electrochem/     # GCD cycling, dQ/dV, CV, and EIS impedance
├── kinetics/        # Reaction rate fitting, Arrhenius, JMAK, energy profiles
├── core/            # Signal smoothing (Savitzky-Golay, ALS), peak detection, fitting
├── structure/       # CIF parsing, space groups, lattice transformations
├── md/              # Trajectory RDF, MSD, diffusion coefficients
└── io/              # Tabular data ingestion and structure export
```

For full API signatures and parameter tables, see [references/api_reference.md](./references/api_reference.md).

---

## Standard Runbooks & Workflows

### 1. DFT Post-Processing: Bader Charge Analysis
Extract and calibrate Bader charges from CP2K calculations or Multiwfn outputs:

```python
from my_sci_toolkit.simulation.cp2k import (
    parse_cp2k_hirshfeld_charges,
    load_bader_charges,
    calibrate_bader_from_hirshfeld,
)

# Option A: Parse Hirshfeld charges directly from CP2K log
hirsh_df = parse_cp2k_hirshfeld_charges("calc.out")

# Option B: Calibrate topological Bader charges from Hirshfeld net charges
valences = {"U": 14.0, "O": 6.0, "Ti": 12.0, "F": 7.0}
bader_calibrated = calibrate_bader_from_hirshfeld(hirsh_df, atom_valences=valences)

# Option C: Load directly from Multiwfn/baderkit output CSV/JSON
bader_df = load_bader_charges("bader_charges.csv")
```

### 2. Publication-Grade Figure Styling (Nature / JACS Standard)
Enforce publication typography, axis tick marks, and color palettes:

```python
import matplotlib.pyplot as plt
from my_sci_toolkit.viz import set_pub_style, PALETTES

# Apply Nature/JACS styling: Arial font, tick marks inside, clean white background
set_pub_style(font_family="Arial", font_size=8, dpi=600)

fig, ax = plt.subplots(figsize=(3.3, 2.5), dpi=600)
# Use curated scientific palettes: PALETTES["nature"], PALETTES["jacs"], etc.
ax.plot(x, y, color=PALETTES["nature"][0], lw=1.2, label="Sample A")
ax.set_xlabel("Energy (eV)")
ax.set_ylabel("Intensity (a.u.)")
fig.savefig("figure_pub.png", dpi=600, bbox_inches="tight")
```

### 3. Assembling Multi-Panel Figures
Compose multiple subplots with standardized labels (a, b, c, d) and unified DPI:

```python
from my_sci_toolkit.viz import assemble_collage

panels = [
    {"image": "fig_a.png", "label": "a"},
    {"image": "fig_b.png", "label": "b"},
    {"image": "fig_c.png", "label": "c"},
    {"image": "fig_d.png", "label": "d"},
]
# Assemble a 2x2 publication collage at 600 DPI
assemble_collage(panels, layout=(2, 2), output_path="Figure_composite.png", dpi=600)
```

### 4. Battery Cycling & Differential Capacity ($dQ/dV$)
```python
from my_sci_toolkit.electrochem import calculate_dqdv, plot_charge_discharge

# Calculate dQ/dV with smoothing
dqdv_df = calculate_dqdv(voltage=v_data, capacity=q_data, window_length=15, polyorder=3)
```

### 5. Spectroscopy Multi-Peak Deconvolution (XRD / Raman / FTIR)
```python
from my_sci_toolkit.spectro.vibrational import fit_peaks
from my_sci_toolkit.core.signal import baseline_als

# Subtract baseline using Asymmetric Least Squares
corrected_y = baseline_als(raw_y, lam=1e5, p=0.01)

# Fit overlapping peaks with Voigt/Gaussian profiles
fit_result = fit_peaks(x_data, corrected_y, model="voigt", peak_guesses=[520.0, 545.0])
```

---

## Agent Guidelines for Scientific Rigor

1. **Physical Conservation Laws**: Ensure total Bader charge neutralizes the overall cell charge (or net ionic balance) when performing slab or cluster analyses.
2. **Fermi Level Alignment**: Always align PDOS / LPDOS energy axes to the Fermi energy ($E - E_F = 0$) and specify the energy unit (eV).
3. **Figure Resolution**: Default all final exported figures to **600 DPI** (`.tif` or `.png`) with transparent or pure white backgrounds.
4. **Reproducibility**: When scripting data processing or plotting workflows, write self-contained Python scripts that can be re-run directly via CLI.
