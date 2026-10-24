# chem-scitoolkit: Modern Scientific Computing & Publication Graphics Toolkit

[![CI](https://github.com/Tuzhidingdong/chem-scitoolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Tuzhidingdong/chem-scitoolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

`chem-scitoolkit` (`my_sci_toolkit`) is a modular, high-cohesion Python package designed for chemical reaction kinetics, spectroscopic analysis, battery electrochemistry, molecular simulation workflows (CP2K, VASP, ORCA, Multiwfn, LAMMPS), and **Nature/JACS-grade publication visualization**.

It natively includes a **Natural Language Interface** powered by either **free, local open-source LLMs** (e.g., Ollama running `qwen2.5-coder`, `llama3.1`) or deterministic offline semantic rule routing.

---

## Table of Contents

- [1. Installation & Distribution](#1-installation--distribution)
  - [1.1 GitHub One-Line Direct Install](#11-github-one-line-direct-install)
  - [1.2 Local Development Installation](#12-local-development-installation)
  - [1.3 PyPI Release Preparation](#13-pypi-release-preparation)
- [2. Natural Language Interface (Free Local LLMs)](#2-natural-language-interface-free-local-llms)
  - [2.1 Running with Local Ollama (Zero Cost, No API Key)](#21-running-with-local-ollama-zero-cost-no-api-key)
  - [2.2 CLI Usage](#22-cli-usage)
  - [2.3 Python API Agent Usage](#23-python-api-agent-usage)
- [3. Complete API Feature Index](#3-complete-api-feature-index)
  - [3.1 `kinetics`: Reaction Dynamics & Thermodynamics](#31-kinetics-reaction-dynamics--thermodynamics)
  - [3.2 `simulation`: Multi-Code Quantum & MD Builders (CP2K, VASP, ORCA, Multiwfn, LAMMPS)](#32-simulation-multi-code-quantum--md-builders-cp2k-vasp-orca-multiwfn-lammps)
  - [3.3 `electrochem`: Battery Cycling & Impedance Analysis](#33-electrochem-battery-cycling--impedance-analysis)
  - [3.4 `spectro`: Spectroscopy Deconvolution (XRD, FTIR, Raman, XPS, EPR)](#34-spectro-spectroscopy-deconvolution-xrd-ftir-raman-xps-epr)
  - [3.5 `viz`: Publication Figure Styling (Nature / JACS)](#35-viz-publication-figure-styling-nature--jacs)
  - [3.6 `core` & `io`: Vectorized Algorithms & Safe File Handling](#36-core--io-vectorized-algorithms--safe-file-handling)
  - [3.7 `structure` & `md`: Crystallography & Trajectory Metrics](#37-structure--md-crystallography--trajectory-metrics)
- [4. Python Code Examples](#4-python-code-examples)
- [5. License](#5-license)

---

## 1. Installation & Distribution

### 1.1 GitHub One-Line Direct Install

Colleagues and researchers can install the package directly into any Python environment with a single terminal command:

```bash
# Core installation (includes numpy, scipy, pandas, matplotlib)
pip install git+https://github.com/Tuzhidingdong/chem-scitoolkit.git

# With electronic structure & crystallography extensions (pymatgen, ase)
pip install "chem-scitoolkit[chem] @ git+https://github.com/Tuzhidingdong/chem-scitoolkit.git"

# Full installation with all optional features (MDAnalysis, impedance, AI support)
pip install "chem-scitoolkit[all] @ git+https://github.com/Tuzhidingdong/chem-scitoolkit.git"
```

### 1.2 Local Development Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Tuzhidingdong/chem-scitoolkit.git
cd chem-scitoolkit
pip install -e ".[dev,all]"
```

### 1.3 PyPI Release Preparation

To publish standard distribution wheels to the Python Package Index:

```bash
# 1. Install build & upload tools
pip install --upgrade build twine

# 2. Build source archive and binary wheel
python -m build

# 3. Verify archive metadata
twine check dist/*

# 4. Upload to PyPI
twine upload dist/*
```

---

## 2. Natural Language Interface (Free Local LLMs)

The toolkit features a built-in AI Agent that converts natural language requests into precise scientific function calls and publication figures.

### 2.1 Running with Local Ollama (Zero Cost, No API Key)

You do **not** need a paid API key. You can use free open-source models running locally on your workstation:

```bash
# 1. Install and launch Ollama (https://ollama.com)
# 2. Pull your preferred coding or reasoning model:
ollama run qwen2.5-coder
```

`chem-scitoolkit` automatically discovers the local Ollama service (`http://localhost:11434/v1`) and routes user prompts through it. If Ollama is offline, the agent gracefully falls back to deterministic rule matching.

### 2.2 CLI Usage

After installation, use the `my-sci` command line tool directly:

```bash
# List all registered scientific tools
my-sci --list-tools

# Natural language prompt execution
my-sci "Plot comparison kinetics of 40min capillary vs 26h bulk water oxidation"

# Build CP2K calculation card from a CIF crystal structure
my-sci "Build cp2k input file from structure aimd.cif"

# Dry-run preview mode (verifies parameter extraction without file execution)
my-sci "Generate reaction intermediate free energy step diagram" --dry-run
```

### 2.3 Python API Agent Usage

```python
from my_sci_toolkit import Agent

# Initialize agent (auto discovers local Ollama / OpenAI endpoints / offline rules)
agent = Agent(backend="auto", output_dir="./outputs")

# Execute natural language command
res = agent.run("Plot comparison kinetics of 40min capillary vs 26h bulk water oxidation")
print("Saved figure artifact:", res["artifact"])
```

---

## 3. Complete API Feature Index

### 3.1 `kinetics`: Reaction Dynamics & Thermodynamics

| Function / API | Key Parameters | Description | Example Usage |
|---|---|---|---|
| `plot_free_energy_profile` | `pathways: dict, step_labels: list, energy_unit="eV"` | Plots publication step diagrams for reaction coordinates (HER, CO2RR, OER) | `plot_free_energy_profile({"Path A": [0, -0.4, 0.2, -0.7]})` |
| `fit_reaction_kinetics` | `time_series, concentration_ratio, order=None` | Fits nonlinear decay kinetics, estimating rate constant $k$ and reaction order $n$ | `res = fit_reaction_kinetics(t, c_c0, order=1)` |
| `fit_arrhenius_activation_energy` | `temperatures_kelvin, rate_constants` | Arrhenius regression calculating activation energy $E_a\ (\text{kJ/mol})$ and factor $A$ | `res = fit_arrhenius_activation_energy([298, 313, 333], [0.01, 0.03, 0.09])` |
| `simulate_nucleation_growth` | `rate_constants=(k_n, k_gt, k_ga), duration=600, dt=1.0` | Solves coupled solid-state nucleation and growth ODE for extent $\alpha(t)$ | `t, a = simulate_nucleation_growth([0.05, 0.0, 0.0], duration=60)` |
| `capillary_pressure` | `surface_tension_gamma=0.0728, contact_angle_deg=0, pore_diameter_m=5e-9` | Calculates capillary hydrostatic negative pressure $-\Delta P_{\text{cap}}\ (\text{kPa})$ | `p_kpa = capillary_pressure(pore_diameter_m=4e-9)` |
| `nanoscale_solubility_ratio` | `radius_nm, surface_energy_J_m2=1.0, molar_volume_m3_mol=3.4e-5` | Ostwald-Freundlich nanoscale crystal solubility enhancement ratio | `ratio = nanoscale_solubility_ratio(radius_nm=2.5)` |
| `first_order_decay` | `t, k` | Analytical 1st-order decay function: $C/C_0 = \exp(-kt)$ | `y = first_order_decay(t, k=0.05)` |
| `nth_order_decay` | `t, k, n` | Analytical $n$-th order decay function | `y = nth_order_decay(t, k=0.05, n=1.5)` |
| `avrami_nucleation` | `t, k, n` | JMAK phase transformation equation: $\alpha = 1 - \exp(-k t^n)$ | `a = avrami_nucleation(t, k=0.001, n=2.5)` |
| `pseudo_second_order` | `t, k2, qe` | Pseudo-second-order adsorption kinetics equation | `qt = pseudo_second_order(t, k2=0.02, qe=120)` |

---

### 3.2 `simulation`: Multi-Code Quantum & MD Builders (CP2K, VASP, ORCA, Multiwfn, LAMMPS)

| Module / API | Key Parameters | Description | Example Usage |
|---|---|---|---|
| `cp2k.build_cp2k_from_cif` | `cif_path, output_inp="cp2k.inp", run_type="GEO_OPT", functional="PBE"` | Reads crystal CIF and builds complete production CP2K input cards | `build_cp2k_from_cif("aimd.cif", "cp2k.inp")` |
| `cp2k.CP2KInputBuilder` | `project_name, run_type, functional, cutoff_ry=400` | Modular CP2K input builder with OT, QS, and basis configurations | `CP2KInputBuilder().build_from_structure(cell, atoms)` |
| `cp2k.generate_distance_colvar` | `atom_a, atom_b, colvar_id=1` | Generates CP2K collective variable (COLVAR) blocks for metadynamics | `block = generate_distance_colvar(1, 2)` |
| `cp2k.CP2KParser` | `log_path: str \| Path` | Extracts final total energies, SCF iteration histories, and convergence states | `e = CP2KParser("cp2k.out").get_final_energy()` |
| `vasp.write_vasp_inputs` | `output_dir, incar_params=None, kpoints_mesh=(3,3,1)` | Automatically creates clean VASP INCAR and KPOINTS files | `write_vasp_inputs("./calc", incar_params={"ENCUT": 500})` |
| `vasp.VASPParser` | `log_path: str \| Path` | Parses OUTCAR & OSZICAR to extract ionic step trajectories and TOTEN | `e_tot = VASPParser("OUTCAR").get_final_energy()` |
| `orca.write_orca_input` | `output_path, atoms, method="B3LYP", basis="def2-SVP", task="Opt Freq"` | Creates complete ORCA molecular input cards with CPCM solvation | `write_orca_input("orca.inp", atoms, task="Opt Freq")` |
| `orca.ORCAParser` | `log_path: str \| Path` | Parses ORCA output logs to extract harmonic vibrational frequencies | `freqs = ORCAParser("orca.out").parse_vibrational_frequencies()` |
| `multiwfn.MultiwfnRunner` | `custom_path=None` | Auto-detects local Multiwfn.exe binary and executes headless batch workflows | `runner = MultiwfnRunner(); res = runner.run_commands(...)` |
| `multiwfn.run_bader_charge_analysis` | `cube_file, multiwfn_path=None` | Automates Multiwfn Basin analysis for Bader atomic charge integration | `run_bader_charge_analysis("density.cube")` |
| `multiwfn.calculate_cohp_fragments` | `wfn_file, fragment_1="e Fe", fragment_2="e Te", energy_range="-12,4,2"` | Automates crystal orbital Hamilton population (COHP) between two fragments | `calculate_cohp_fragments("aimd.wfn", "e Fe", "e Te")` |
| `lammps.write_lammps_data` | `output_path, box_bounds, atoms, masses, title=...` | Writes full-style standard LAMMPS *.data coordinate and topology files | `write_lammps_data("system.data", box, atoms, masses)` |
| `lammps.LAMMPSInputBuilder` | `data_file, timestep_fs=1.0, ensemble="nvt", steps=50000` | Builds control scripts for TIP4P/2005 water models and classical MD | `LAMMPSInputBuilder().build_tip4p_water_script()` |
| `ml_potentials.generate_mace_training_command` | `name, train_file, valid_file, r_max=5.0, batch_size=16` | Generates CLI training commands for MACE equivariant neural potentials | `cmd = generate_mace_training_command(...)` |
| `slurm.generate_slurm_script` | `job_name, software="cp2k", nodes=1, ntasks_per_node=64` | Generates high-performance computing cluster submission scripts (*.sh) | `generate_slurm_script("opt", software="cp2k", nodes=2)` |

---

### 3.3 `electrochem`: Battery Cycling & Impedance Analysis

| Function / API | Key Parameters | Description | Example Usage |
|---|---|---|---|
| `plot_charge_discharge` | `capacity_mah_g, voltage_v, cycle_index=1, c_rate="0.1C"` | Plots standard galvanostatic charge/discharge voltage profiles | `plot_charge_discharge(q, v, c_rate="0.2C")` |
| `calculate_dqdv` | `voltage, capacity, smooth_window=15` | Calculates differential capacity $dQ/dV\ (\text{mAh}\cdot\text{g}^{-1}\cdot\text{V}^{-1})$ | `v_s, dqdv = calculate_dqdv(v, q)` |
| `plot_cycling_stability` | `cycles, discharge_capacity, coulombic_efficiency=None` | Dual Y-axis cycling retention and Coulombic Efficiency curves | `plot_cycling_stability(cycles, cap, ce)` |
| `plot_cv_curve` | `potential_v, current_ma, scan_rate_mv_s=None` | Cyclic voltammetry (CV) representation with zero baseline alignment | `plot_cv_curve(pot, cur, scan_rate_mv_s=50)` |
| `plot_nyquist_eis` | `z_real_ohm, z_imag_ohm` | Standard equal-aspect-ratio Nyquist plot ($-Z''$ vs $Z'$) | `plot_nyquist_eis(z_re, z_im)` |
| `active_material_moles` | `mass_active_g, molecular_weight_g_mol` | Converts active electrode mass to molar quantity | `n_mol = active_material_moles(0.015, 96.0)` |
| `theoretical_specific_capacity` | `n_electrons, molecular_weight_g_mol` | Calculates theoretical capacity ($\text{mAh/g}$) based on Faraday's law | `q_th = theoretical_specific_capacity(1, 157.7)` |

---

### 3.4 `spectro`: Spectroscopy Deconvolution (XRD, FTIR, Raman, XPS, EPR)

| Function / API | Key Parameters | Description | Example Usage |
|---|---|---|---|
| `plot_xrd_pattern` | `two_theta, intensity, baseline_corr=True, normalize=True` | Publication 1D XRD diffraction patterns with baseline subtraction | `plot_xrd_pattern(two_theta, inten)` |
| `plot_xrd_stack` | `two_theta, intensity_series, labels, offset=0.35` | Vertically stacked waterfall XRD profiles for phase transition tracking | `plot_xrd_stack(2theta, [y1, y2], ["1h", "2h"])` |
| `plot_vibrational_spectrum` | `wavenumber, intensity, spec_type="FTIR", trim_range=None` | FTIR and Raman spectra (FTIR automatically inverts the X-axis) | `plot_vibrational_spectrum(wn, int_ir)` |
| `deconvolute_peaks` | `x, y, initial_centers, initial_widths=None` | Gaussian peak deconvolution with filled sub-bands | `deconvolute_peaks(x, y, [3610, 3640])` |
| `shirley_background` | `x, y, tol=1e-4, max_iter=50` | Iterative Shirley inelastic electron scattering background for XPS | `bg = shirley_background(be, counts)` |
| `plot_epr_spectrum` | `magnetic_field_gauss, first_derivative_signal` | Continuous-wave Electron Paramagnetic Resonance (EPR) 1st derivative plots | `plot_epr_spectrum(field, dI_dB)` |

---

### 3.5 `viz`: Publication Figure Styling (Nature / JACS)

| Function / API | Key Parameters | Description | Example Usage |
|---|---|---|---|
| `plot_completion_time_bar` | `systems, times_h, unit_labels, y_label=...` | Nature-style comparative reaction completion time bar chart | `plot_completion_time_bar(["Capillary", "Bulk"], [0.667, 26], ["40 min", "26 h"])` |
| `plot_decay_curve` | `t_exp, c_exp, t_fit=None, c_fit=None, rate_constant_k=...` | Concentration decay curves with optional error bars and fit overlays | `plot_decay_curve(t, c, t_fit, c_fit, rate_constant_k=0.07)` |
| `plot_conversion_alpha` | `t_exp, alpha_exp, simulations=None` | Reaction progress extent $\alpha(t)$ with multiple simulated trajectories | `plot_conversion_alpha(t, a, simulations=[...])` |
| `create_panel_collage` | `image_paths, rows, cols, labels=None` | Combines multiple figure files into publication composite panels (a, b, c, d) | `create_panel_collage(["f1.png", "f2.png"], 1, 2)` |
| `apply_style` | `theme="nature", font_family="Arial", font_size=8` | Sets global Matplotlib rcParams conforming to Nature/JACS guidelines | `apply_style(theme="nature")` |
| `get_figure_dimensions` | `columns="single", aspect_ratio=0.80` | Computes exact single-column (3.5 in) or double-column (7.2 in) dimensions | `w, h = get_figure_dimensions("single")` |

---

### 3.6 `core` & `io`: Vectorized Algorithms & Safe File Handling

- `normalize_sum(arr)`: Normalizes array so $\sum y_i = 1.0$.
- `normalize_minmax(arr)`: Linearly rescales array to $[0.0, 1.0]$.
- `baseline_correct(intensity, degree=2)`: Vectorized modified polynomial baseline correction.
- `smooth_spectrum(y, window_length=9)`: Savitzky-Golay digital filtering.
- `read_xy(path)`: Fast two-column tabular spectrum ingestion.
- `read_xy_series_dir(dir)`: Sequentially reads time-resolved spectra from a folder.
- `save_publication_figure(fig, path, dpi=600)`: 600 DPI publication exporter with transparent background.
- `pdb_to_xyz(input_pdb, output_xyz)` / `xyz_to_pdb(input_xyz, output_pdb)`: Pure Python structure conversions.

---

### 3.7 `structure` & `md`: Crystallography & Trajectory Metrics

- `calculate_d_spacing(crystal_system, a, b, c, h, k, l)`: Analytical metric tensor calculator for interplanar spacing $d_{hkl}\ (\text{Å})$ across cubic, tetragonal, orthorhombic, hexagonal, and monoclinic lattices.
- `calculate_diffusion_coefficient(time_ps, msd_angstrom2, dim=3)`: Extracts self-diffusion coefficient $D\ (10^{-9}\ \text{m}^2/\text{s})$ from MSD trajectories using Einstein's relation.

---

## 4. Python Code Examples

```python
from my_sci_toolkit import (
    plot_completion_time_bar,
    plot_conversion_alpha,
    simulate_nucleation_growth,
    build_cp2k_from_cif,
    Agent,
)

# 1. Plot 40min capillary vs 26h bulk water oxidation completion comparison
fig = plot_completion_time_bar(
    systems=["Capillary", "Bulk water", "Air"],
    times_h=[40.0 / 60.0, 26.0, 280.0],
    unit_labels=["40 min", "26 h", "280 h"],
    save_path="./outputs/completion_comparison.png",
)

# 2. Coupled solid-state nucleation and growth simulation
t_fast, alpha_fast = simulate_nucleation_growth(rate_constants=[0.05, 0.0, 0.0], duration=60.0)
t_slow, alpha_slow = simulate_nucleation_growth(rate_constants=[0.001, 0.0, 0.0], duration=60.0)

fig_alpha = plot_conversion_alpha(
    t_exp=[0, 10, 20, 30, 40, 50, 60],
    alpha_exp=[0.0, 0.25, 0.58, 0.82, 0.98, 1.0, 1.0],
    simulations=[
        {"t": t_fast, "alpha": alpha_fast, "label": "Capillary (Fast)", "color": "#C0392B"},
        {"t": t_slow, "alpha": alpha_slow, "label": "Bulk (Slow)", "color": "#2980B9"},
    ],
    save_path="./outputs/conversion_alpha.png",
)

# 3. Build CP2K input file directly from crystal structure
build_cp2k_from_cif("aimd.cif", output_inp="./outputs/cp2k.inp", run_type="GEO_OPT")

# 4. Natural language agent execution with free local LLM
agent = Agent(backend="auto")
agent.run("Plot comparison kinetics of 40min capillary vs 26h bulk water oxidation")
```

---

## 5. License

Distributed under the terms of the [MIT License](LICENSE).
Copyright (c) 2026 Scientific Computing & AI Chemistry Team.
