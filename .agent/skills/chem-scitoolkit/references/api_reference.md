# chem-scitoolkit Complete API Reference

This reference documents the modules, classes, and primary functions available in `chem-scitoolkit` (`my_sci_toolkit`).

---

## 1. Simulation (`my_sci_toolkit.simulation`)

### 1.1 CP2K (`my_sci_toolkit.simulation.cp2k`)
- **`CP2KInputBuilder(calc_type="GEO_OPT", project_name="cp2k_calc", ...)`**:
  - Builds structured CP2K `.inp` files for geometry optimization, cell optimization, and molecular dynamics.
  - Supports Quickstep DFT, GAPW, GPW, DZVP-MOLOPT basis sets, and GTH pseudopotentials.
  - Generates periodic Poisson solvers, OT (Orbital Transformation) or diagonalization preconditioners.
- **`build_cp2k_from_cif(cif_path, output_inp_path, ...)`**:
  - Automatically parses crystal structures from `.cif` and configures cell parameters and atomic coordinates.
- **`parse_cp2k_hirshfeld_charges(log_path)`**:
  - Extracts atomic Hirshfeld charges, alpha/beta populations, and spin moments into a pandas DataFrame.
- **`load_bader_charges(charges_path)`**:
  - Ingests Bader charges from `bader_charges.csv` or `baderkit_results.json`.
- **`calibrate_bader_from_hirshfeld(hirshfeld_df, atom_valences, scaling_factors=None)`**:
  - Calibrates QTAIM topological Bader charges using self-consistent Hirshfeld populations and atomic valence electrons with lattice charge neutrality preservation.
- **`read_cp2k_energy_trajectory(ener_file_path)`**:
  - Parses `.ener` files returning `(time_ps, temp_k, total_energy_au)`.
- **`read_cp2k_colvar(colvar_file_path)`**:
  - Reads collective variable trajectories for metadynamics or biased simulations.

### 1.2 VASP (`my_sci_toolkit.simulation.vasp`)
- **`VASPInputBuilder`**: Generates INCAR, KPOINTS, POSCAR, and POTCAR configuration blocks.
- **`VASPParser`**: Parses OUTCAR, OSZICAR, and `vasprun.xml` for SCF convergence, forces, and final energy.

### 1.3 ORCA (`my_sci_toolkit.simulation.orca`)
- **`ORCAInputBuilder`**: Assembles ORCA input files supporting DFT (B3LYP, PBE0, wB97X-D3), MP2, DLPNO-CCSD(T), and implicit solvation (CPCM/SMD).
- **`ORCAParser`**: Extracts final single-point energies, harmonic frequencies, and thermochemical corrections (zero-point energy, enthalpy, Gibbs free energy).

### 1.4 Multiwfn (`my_sci_toolkit.simulation.multiwfn`)
- **`MultiwfnRunner`**: Batch execution wrapper for automated Multiwfn analyses.
- **`charge_bader`**: Computes Bader partition grids from electron density cube files (`.cube`).
- **`cohp_dos`**: Generates DOS, PDOS, COHP, and COOP curves from wavefunction files (.fchk, .molden).

### 1.5 LAMMPS (`my_sci_toolkit.simulation.lammps`)
- **`LAMMPSInputBuilder`**: Generates `.in` scripts for NVE, NVT, NPT MD simulations with thermostating/barostating.
- **`LAMMPSDataBuilder`**: Generates data topology files from coordinate structures.

### 1.6 Machine-Learned Interatomic Potentials (`my_sci_toolkit.simulation.ml_potentials`)
- **`training`**: Formats datasets for NEP (GPUMD), NequIP, MACE, and DeepMD.
- **`ase_dynamics`**: ASE calculator wrapper to run MLIP molecular dynamics.

### 1.7 Slurm HPC Integration (`my_sci_toolkit.simulation.slurm`)
- **`generate_slurm_script(job_name, nodes, ntasks, partition, time, commands)`**:
  - Generates ready-to-submit `.slurm` or `.sh` submission scripts for high-performance computing clusters.

---

## 2. Visualization (`my_sci_toolkit.viz`)

### 2.1 Style & Palettes (`my_sci_toolkit.viz.style`)
- **`set_pub_style(font_family="Arial", font_size=8, dpi=600)`**:
  - Configures matplotlib rcParams for publication: tick marks inside, sans-serif fonts, high DPI.
- **`PALETTES`**:
  - Curated color dictionaries: `PALETTES["nature"]`, `PALETTES["jacs"]`, `PALETTES["muted"]`, `PALETTES["science"]`.

### 2.2 Plotting (`my_sci_toolkit.viz.plots`)
- **`plot_completion_time_bar(categories, values, errors=None, ...)`**: Publication bar charts with error bars and value labels.
- **`plot_decay_curve(t, y, fit_y=None, ...)`**: Reaction/decay time-series plots.
- **`plot_conversion_alpha(t, alpha, ...)`**: Kinetic conversion degree curves.

### 2.3 Collage & Panel Assembly (`my_sci_toolkit.viz.collage`)
- **`assemble_collage(panels, layout, output_path, dpi=600, labels="a,b,c...")`**:
  - Combines individual figure panels into a unified multi-panel figure with aligned subplot indices.

---

## 3. Electrochemistry (`my_sci_toolkit.electrochem`)

- **`plot_charge_discharge(df, cycle_col, v_col, q_col, cycles_to_plot=[1, 2, 5, 10])`**:
  - Visualizes GCD voltage profiles across specific cycle numbers.
- **`calculate_dqdv(voltage, capacity, window_length=15, polyorder=3)`**:
  - Computes differential capacity $dQ/dV$ curves with Savitzky-Golay derivative filtering to identify redox peaks.
- **`fit_nyquist_eis(freq, z_real, z_imag, circuit_model="R-C-R")`**:
  - Fits impedance spectra to extract charge-transfer resistance ($R_{\text{ct}}$) and SEI film resistance ($R_{\text{sei}}$).

---

## 4. Spectroscopy (`my_sci_toolkit.spectro`)

- **`plot_xrd_pattern(two_theta, intensity, hkl_labels=None)`**:
  - Formats XRD diffraction patterns with standard $2\theta$ angles.
- **`plot_xrd_stack(patterns_list, offset=100.0)`**:
  - Waterfall stacked plots for in-situ or multi-sample XRD.
- **`calculate_scherrer_size(two_theta_deg, fwhm_deg, wavelength_angstrom=1.5406)`**:
  - Computes mean crystallite domain size using the Scherrer equation.
- **`fit_peaks(x, y, model="voigt", peak_guesses=None)`**:
  - Deconvolutes overlapping vibrational/optical peaks (FTIR, Raman, XPS).

---

## 5. Kinetics & Thermodynamics (`my_sci_toolkit.kinetics`)

- **`fit_reaction_kinetics(time, concentration, order=1)`**:
  - Computes rate constants ($k$), determination coefficient ($R^2$), and half-life ($t_{1/2}$).
- **`fit_arrhenius_activation_energy(temperatures_k, rate_constants)`**:
  - Fits $\ln k \text{ vs } 1/T$ to derive activation energy ($E_a$) and pre-exponential factor ($A$).
- **`simulate_nucleation_growth(time, k, n)`**:
  - Simulates phase transformation kinetics using the Avrami-Erofeev / JMAK model ($\alpha(t) = 1 - \exp(-(kt)^n)$).
- **`ReactionEnergyProfile(intermediates, energies)`**:
  - Generates reaction pathway energy diagrams with transition states ($\text{TS}$) and reaction intermediates.
