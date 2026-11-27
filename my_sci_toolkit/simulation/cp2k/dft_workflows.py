"""Task-aware CP2K output, charge, PDOS, cube and ASE thermochemistry interfaces."""
from __future__ import annotations

import hashlib
import io
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd


def validate_cp2k_output(log_path: str | Path, run_type: str) -> dict[str, Any]:
    """Validate program termination, SCF and task-specific records independently of scheduler state."""
    path = Path(log_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    task = str(run_type).upper()
    if task not in {"ENERGY", "ENERGY_FORCE", "GEO_OPT"}:
        raise ValueError("run_type must be ENERGY, ENERGY_FORCE or GEO_OPT")
    version_match = re.search(r"CP2K version\s+([^\s(]+)", text, re.IGNORECASE)
    energies = re.findall(
        r"ENERGY\|\s+Total FORCE_EVAL\s+\(\s*QS\s*\)\s+energy\s+\(a\.u\.\):\s*([-+0-9.Ee]+)",
        text, re.IGNORECASE,
    )
    final_energy = float(energies[-1]) if energies else None
    normal = bool(re.search(r"PROGRAM ENDED AT", text, re.IGNORECASE))
    fatal = [
        line.strip() for line in text.splitlines()
        if re.search(r"ABORT\||\*\*\*\s*ERROR|FATAL ERROR", line, re.IGNORECASE)
    ]
    warning_lines = [
        line.strip() for line in text.splitlines()
        if re.search(r"\bWARNING\b", line, re.IGNORECASE)
    ]
    scf = bool(re.search(r"SCF run converged", text, re.IGNORECASE))
    geo_done = bool(re.search(r"GEOMETRY OPTIMIZATION COMPLETED", text, re.IGNORECASE))
    forces = bool(re.search(r"ATOMIC FORCES\s+in", text, re.IGNORECASE))
    max_force = bool(re.search(r"MAXIMUM FORCE", text, re.IGNORECASE))
    rms_force = bool(re.search(r"RMS FORCE", text, re.IGNORECASE))
    if task == "ENERGY":
        task_records = final_energy is not None
        geo_result = force_result = force_metrics = None
    elif task == "ENERGY_FORCE":
        task_records = final_energy is not None and forces
        geo_result = None
        force_result = forces
        force_metrics = None
    else:
        task_records = final_energy is not None and geo_done and max_force and rms_force
        geo_result = geo_done
        force_result = forces
        force_metrics = max_force and rms_force
    passed = normal and scf and task_records and not fatal
    return {
        "run_type": task,
        "status": "passed" if passed else "failed_or_incomplete",
        "program_normal_termination": normal,
        "output_complete": normal,
        "scf_converged": scf,
        "geometry_optimization_completed": geo_result,
        "atomic_forces_present": force_result,
        "final_force_metrics_present": force_metrics,
        "final_energy_hartree": final_energy,
        "fatal_error_count": len(fatal),
        "fatal_errors": fatal,
        "warning_count": len(warning_lines),
        "warnings": warning_lines,
        "cp2k_version": version_match.group(1) if version_match else None,
        "parser_version": "chem-scitoolkit-task-validator/1.0.0",
    }


def estimate_hirshfeld_charges(
    hirshfeld_df: pd.DataFrame,
    *,
    valence_electrons: Mapping[str, float],
    scaling_factors: Mapping[str, float],
) -> pd.DataFrame:
    """Return an approximate calibrated Hirshfeld estimate; it is not a Bader result."""
    required = {"atom_id", "element", "net_charge"}
    if not required.issubset(hirshfeld_df.columns):
        raise ValueError(f"Hirshfeld table is missing columns: {sorted(required - set(hirshfeld_df.columns))}")
    if not valence_electrons or not scaling_factors:
        raise ValueError("explicit valence_electrons and scaling_factors are required")
    result = hirshfeld_df.copy()
    charges, populations = [], []
    for row in result.itertuples(index=False):
        element = str(getattr(row, "element"))
        if element not in valence_electrons or element not in scaling_factors:
            raise ValueError(f"missing explicit calibration for element {element!r}")
        charge = float(getattr(row, "net_charge")) * float(scaling_factors[element])
        valence = float(valence_electrons[element])
        if not math.isfinite(charge + valence):
            raise ValueError(f"non-finite calibration for element {element!r}")
        charges.append(charge)
        populations.append(valence - charge)
    result["estimated_hirshfeld_population"] = populations
    result["estimated_hirshfeld_net_charge"] = charges
    result["charge_method"] = "approximate_calibrated_hirshfeld_estimate"
    result["charge_residual"] = float(sum(charges))
    return result


def validate_bader_true_results(
    results: pd.DataFrame,
    *,
    expected_atoms: Sequence[tuple[int, str]],
    expected_electron_count: float | None = None,
    tolerance: float = 1.0e-3,
) -> dict[str, Any]:
    """Validate imported density-basin populations without redistributing residual charge."""
    required = {"atom_id", "element", "bader_population"}
    if not required.issubset(results.columns):
        raise ValueError(f"Bader result lacks columns: {sorted(required - set(results.columns))}")
    if len(results) != len(expected_atoms):
        raise ValueError("Bader atom count does not match the input structure")
    observed = list(zip(results["atom_id"].astype(int), results["element"].astype(str)))
    if observed != list(expected_atoms):
        raise ValueError("Bader atom order or element mapping does not match the input structure")
    populations = pd.to_numeric(results["bader_population"], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(populations).all():
        raise ValueError("Bader populations contain non-finite values")
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")
    total = float(populations.sum())
    residual = None if expected_electron_count is None else total - float(expected_electron_count)
    if residual is not None and abs(residual) > tolerance:
        raise ValueError("Bader electron-population residual exceeds tolerance")
    return {
        "method": "true_bader_density_basin",
        "atom_count": len(results),
        "electron_population_sum": total,
        "expected_electron_count": expected_electron_count,
        "population_residual": residual,
        "tolerance": tolerance,
        "passed": residual is None or abs(residual) <= tolerance,
    }


def normalize_cp2k_pdos(
    pdos_paths: Sequence[str | Path],
    *,
    sigma_hartree: float = 0.02,
    grid_step_hartree: float = 0.001,
    energy_alignment: str = "fermi",
    vacuum_minus_fermi_eV: float | None = None,
    vacuum_plateau_validated: bool = False,
    spin_channels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Delegate PDOS broadening to cp2k-output-tools; preserve projections and source hashes."""
    executable = shutil.which("cp2k_pdos")
    if executable is None:
        raise FileNotFoundError("cp2k-output-tools is optional; executable cp2k_pdos was not found")
    paths = [Path(item) for item in pdos_paths]
    if not paths or any(not item.is_file() for item in paths):
        raise FileNotFoundError("all supplied CP2K PDOS files must exist")
    if sigma_hartree <= 0 or grid_step_hartree <= 0:
        raise ValueError("sigma_hartree and grid_step_hartree must be positive")
    mode = str(energy_alignment).lower()
    if mode not in {"fermi", "vacuum"}:
        raise ValueError("energy_alignment must be 'fermi' or 'vacuum'")
    if mode == "vacuum" and (
        vacuum_minus_fermi_eV is None or not vacuum_plateau_validated
        or not math.isfinite(float(vacuum_minus_fermi_eV))
    ):
        raise ValueError("vacuum alignment requires a validated plateau and explicit vacuum_minus_fermi_eV")
    channels = list(spin_channels or ["unspecified"] * len(paths))
    if len(channels) != len(paths):
        raise ValueError("spin_channels length must match the PDOS file count")
    command = [
        executable, "--sigma", str(sigma_hartree), "--de", str(grid_step_hartree),
        *[str(item) for item in paths],
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"cp2k_pdos failed with exit code {completed.returncode}: {completed.stderr[-2000:]}"
        )
    frame = pd.read_csv(io.StringIO(completed.stdout), sep=r"\s+")
    energy_col = next((col for col in frame.columns if str(col).lower() in {"energy_[ev]", "energy_ev"}), None)
    if energy_col is None:
        raise ValueError("cp2k_pdos output is missing the Energy_[eV] column")
    energies = pd.to_numeric(frame[energy_col], errors="coerce").to_numpy(dtype=float)
    if len(energies) < 2 or not np.isfinite(energies).all() or not np.all(np.diff(energies) > 0):
        raise ValueError("normalized PDOS energy grid must be finite and strictly increasing")
    if mode == "vacuum":
        frame[energy_col] = energies - float(vacuum_minus_fermi_eV)
    source_hashes = {
        str(item): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in paths
    }
    try:
        import cp2k_output_tools
        parser_version = getattr(cp2k_output_tools, "__version__", "unknown")
    except ImportError:
        parser_version = "unknown"
    return {
        "data": frame,
        "metadata": {
            "parser": "cp2k-output-tools/cp2k_pdos",
            "parser_version": parser_version,
            "source_sha256": source_hashes,
            "energy_unit": "eV",
            "energy_alignment": mode,
            "spin_channels": channels,
            "projection_columns": [str(col) for col in frame.columns if col != energy_col],
            "sigma_hartree": float(sigma_hartree),
            "grid_step_hartree": float(grid_step_hartree),
            "vacuum_minus_fermi_eV": float(vacuum_minus_fermi_eV) if mode == "vacuum" else None,
            "warnings": ["cp2k-output-tools writes E-E_F in eV; projection columns are retained independently."],
        },
    }


def read_cube(path: str | Path) -> dict[str, Any]:
    """Read one scalar Gaussian cube field and retain its geometry/grid metadata."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) < 6:
        raise ValueError("cube file is truncated before its grid header")
    atom_fields = lines[2].split()
    if len(atom_fields) < 4:
        raise ValueError("cube atom-count/origin record is malformed")
    atom_count_signed = int(atom_fields[0])
    if atom_count_signed < 0:
        raise ValueError("multi-orbital cube files are not supported by this single-field reader")
    atom_count = atom_count_signed
    origin = np.asarray([float(x) for x in atom_fields[1:4]], dtype=float)
    dimensions, vectors = [], []
    for line in lines[3:6]:
        fields = line.split()
        if len(fields) < 4:
            raise ValueError("cube grid-vector record is malformed")
        signed_count = int(fields[0])
        if signed_count == 0:
            raise ValueError("cube grid dimension cannot be zero")
        dimensions.append(abs(signed_count))
        vectors.append([float(x) for x in fields[1:4]])
    atom_records = []
    for line in lines[6:6 + atom_count]:
        fields = line.split()
        if len(fields) < 5:
            raise ValueError("cube atom record is malformed")
        atom_records.append({
            "atomic_number": int(float(fields[0])),
            "nuclear_charge": float(fields[1]),
            "xyz": [float(x) for x in fields[2:5]],
        })
    if len(atom_records) != atom_count:
        raise ValueError("cube file is truncated within its atom records")
    values = []
    for line in lines[6 + atom_count:]:
        values.extend(float(x.replace("D", "E").replace("d", "e")) for x in line.split())
    expected = int(np.prod(dimensions))
    if len(values) != expected:
        raise ValueError(f"cube scalar data size mismatch: expected {expected}, found {len(values)}")
    data = np.asarray(values, dtype=float)
    if not np.isfinite(origin).all() or not np.isfinite(vectors).all() or not np.isfinite(data).all():
        raise ValueError("cube grid metadata or scalar data contains non-finite values")
    return {
        "path": str(source),
        "comments": lines[:2],
        "atom_count": atom_count,
        "origin": origin,
        "grid_dimensions": tuple(dimensions),
        "voxel_vectors": np.asarray(vectors, dtype=float),
        "atoms": atom_records,
        "values": data.reshape(tuple(dimensions)),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }


def validate_cube_compatibility(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    *,
    tolerance: float = 1.0e-8,
) -> dict[str, Any]:
    """Check grid origin, dimensions, voxel vectors and ordered atom records."""
    reasons = []
    if first["grid_dimensions"] != second["grid_dimensions"]:
        reasons.append("grid_dimensions_mismatch")
    if not np.allclose(first["origin"], second["origin"], atol=tolerance, rtol=0):
        reasons.append("origin_mismatch")
    if not np.allclose(first["voxel_vectors"], second["voxel_vectors"], atol=tolerance, rtol=0):
        reasons.append("voxel_vectors_mismatch")
    if first["atom_count"] != second["atom_count"] or len(first["atoms"]) != len(second["atoms"]):
        reasons.append("atom_count_mismatch")
    else:
        for index, (left, right) in enumerate(zip(first["atoms"], second["atoms"])):
            if (
                left["atomic_number"] != right["atomic_number"]
                or not np.allclose(left["xyz"], right["xyz"], atol=tolerance, rtol=0)
            ):
                reasons.append(f"atom_mapping_mismatch_at_{index}")
    return {"compatible": not reasons, "reasons": reasons, "tolerance": tolerance}


def subtract_cube_fields(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    *,
    tolerance: float = 1.0e-8,
) -> np.ndarray:
    """Subtract volumetric fields only after strict grid/atom compatibility checks."""
    report = validate_cube_compatibility(first, second, tolerance=tolerance)
    if not report["compatible"]:
        raise ValueError("incompatible cube grids or atom mappings: " + ", ".join(report["reasons"]))
    return np.asarray(first["values"], dtype=float) - np.asarray(second["values"], dtype=float)


def detect_vacuum_plateau(
    z_coordinates: Sequence[float],
    potential_values: Sequence[float],
    *,
    z_min: float,
    z_max: float,
    max_spread: float,
    max_abs_slope: float,
) -> dict[str, Any]:
    """Assess a user-selected vacuum interval and report measured spread/slope."""
    z = np.asarray(z_coordinates, dtype=float)
    values = np.asarray(potential_values, dtype=float)
    if z.ndim != 1 or values.ndim != 1 or len(z) != len(values) or len(z) < 2:
        raise ValueError("coordinates and potential must be equal-length 1D arrays")
    if not np.isfinite(z).all() or not np.isfinite(values).all():
        raise ValueError("vacuum profile contains non-finite values")
    if z_min >= z_max or max_spread < 0 or max_abs_slope < 0:
        raise ValueError("vacuum interval and tolerances are invalid")
    if not np.all(np.diff(z) > 0):
        raise ValueError("z_coordinates must be strictly increasing")
    selected = (z >= z_min) & (z <= z_max)
    if int(selected.sum()) < 2:
        raise ValueError("vacuum interval contains fewer than two samples")
    z_slice, v_slice = z[selected], values[selected]
    slope = float(np.polyfit(z_slice, v_slice, 1)[0])
    spread = float(v_slice.max() - v_slice.min())
    return {
        "passed": spread <= max_spread and abs(slope) <= max_abs_slope,
        "z_region": [float(z_min), float(z_max)],
        "sample_count": int(selected.sum()),
        "mean_potential": float(v_slice.mean()),
        "spread": spread,
        "slope_per_length_unit": slope,
        "max_spread": float(max_spread),
        "max_abs_slope": float(max_abs_slope),
    }


def validate_vacuum_energy_reference(
    *,
    potential_quantity: str,
    reference_zero: str,
    plateau_report: Mapping[str, Any],
    reference_energy_eV: float | None,
) -> dict[str, Any]:
    """Fail closed unless the electrostatic-potential quantity/zero and plateau are explicit."""
    supported = (
        potential_quantity == "electrostatic_potential"
        and reference_zero == "documented_cp2k_electrostatic_potential_zero"
        and bool(plateau_report.get("passed"))
        and reference_energy_eV is not None
        and math.isfinite(float(reference_energy_eV))
    )
    return {
        "supported": supported,
        "reference_energy_eV": float(reference_energy_eV) if supported else None,
        "reason": None if supported else (
            "vacuum alignment unsupported: require identified electrostatic potential, documented zero, "
            "validated plateau and explicit energy reference"
        ),
    }


def ase_harmonic_thermochemistry(
    frequencies_cm1: Sequence[float],
    *,
    temperature_K: float,
    mode_scope: str,
    selected_atom_indices: Sequence[int] = (),
    frozen_atom_indices: Sequence[int] = (),
    imaginary_mode_policy: str = "error",
    near_zero_cm1: float = 1.0,
) -> dict[str, Any]:
    """Use ASE HarmonicThermo with an explicit adsorbate-subspace or full-system mode scope."""
    if temperature_K <= 0 or not math.isfinite(temperature_K):
        raise ValueError("temperature_K must be positive and finite")
    if mode_scope not in {"adsorbate_subspace", "full_system"}:
        raise ValueError("mode_scope must be adsorbate_subspace or full_system")
    if mode_scope == "adsorbate_subspace" and not selected_atom_indices:
        raise ValueError("adsorbate_subspace requires explicit selected_atom_indices")
    if mode_scope == "full_system" and frozen_atom_indices:
        raise ValueError("full_system cannot also declare frozen support atoms")
    if imaginary_mode_policy not in {"error", "exclude"}:
        raise ValueError("imaginary_mode_policy must be error or exclude")
    values = np.asarray(frequencies_cm1, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("frequencies_cm1 must be a finite 1D sequence")
    imaginary = values[values < -near_zero_cm1]
    near_zero = values[(values >= -near_zero_cm1) & (values <= near_zero_cm1)]
    if len(imaginary) and imaginary_mode_policy == "error":
        raise ValueError("imaginary modes are present; specify an explicit policy")
    accepted = values[values > near_zero_cm1]
    if not len(accepted):
        raise ValueError("no positive vibrational modes remain after filtering")
    try:
        from ase import units
        from ase.thermochemistry import HarmonicThermo
    except ImportError as exc:
        raise ImportError("ASE is optional; install chem-scitoolkit[chem]") from exc
    thermo = HarmonicThermo(vib_energies=accepted * units.invcm)
    zpe = float(thermo.get_ZPE_correction())
    internal = float(thermo.get_internal_energy(float(temperature_K)))
    entropy = float(thermo.get_entropy(float(temperature_K)))
    free_energy = float(thermo.get_helmholtz_energy(float(temperature_K)))
    return {
        "frequencies_cm1": accepted.tolist(),
        "input_frequency_count": int(len(values)),
        "imaginary_mode_count": int(len(imaginary)),
        "near_zero_mode_count": int(len(near_zero)),
        "imaginary_mode_policy": imaginary_mode_policy,
        "temperature_K": float(temperature_K),
        "mode_scope": mode_scope,
        "selected_atom_indices": list(selected_atom_indices),
        "frozen_atom_indices": list(frozen_atom_indices),
        "zpe_eV": zpe,
        "internal_energy_eV": internal,
        "entropy_eV_per_K": entropy,
        "helmholtz_free_energy_eV": free_energy,
        "thermochemistry_engine": "ASE HarmonicThermo",
        "ideal_gas_treatment": False,
        "mode_scope_assumption": "Input frequencies already correspond to the declared selected/frozen-atom subspace.",
    }
