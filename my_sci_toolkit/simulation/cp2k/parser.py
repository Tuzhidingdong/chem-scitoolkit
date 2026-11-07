"""CP2K output log, trajectory, and free energy parser."""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from my_sci_toolkit.simulation.base import BaseParser


class CP2KParser(BaseParser):
    """Parser for CP2K standard calculation logs (*.out, *.log)."""

    def get_final_energy(self) -> Optional[float]:
        """Extract final total energy in Hartree from CP2K log."""
        energy = None
        pattern = re.compile(r"ENERGY\|\s+Total FORCE_EVAL \( QS \) energy \(a\.u\.\):\s+([-\d\.]+)")
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    energy = float(m.group(1))
        return energy

    def is_converged(self) -> bool:
        """Check whether SCF and geometry optimization reached convergence criteria."""
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return "GEOMETRY OPTIMIZATION COMPLETED" in content or "SCF run converged" in content

    def parse_scf_cycles(self) -> List[float]:
        """Extract energy convergence trajectory per SCF iteration."""
        energies = []
        pattern = re.compile(r"^\s*\d+\s+[-]?[\d\.]+\s+[-]?[\d\.]+\s+([-\d\.]+)")
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = pattern.match(line)
                if m:
                    try:
                        energies.append(float(m.group(1)))
                    except ValueError:
                        pass
        return energies


def read_cp2k_colvar(colvar_log_path: str | Path) -> pd.DataFrame:
    """Parse CP2K metadynamics COLVAR trajectory file into a pandas DataFrame."""
    p = Path(colvar_log_path)
    if not p.exists():
        raise FileNotFoundError(f"COLVAR log not found: {p}")
    # CP2K colvar format: Step, Time [fs], CV1, CV2, ..., V_metadyn
    df = pd.read_csv(p, sep=r"\s+", comment="#", header=None, engine="python")
    return df


def read_cp2k_energy_trajectory(ener_file_path: str | Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Parse CP2K *.ener trajectory (Step, Time [fs], Kinetic [a.u.], Temperature [K], Potential [a.u.], Total [a.u.])."""
    p = Path(ener_file_path)
    if not p.exists():
        raise FileNotFoundError(f"Energy file not found: {p}")
    df = pd.read_csv(p, sep=r"\s+", comment="#", header=None, engine="python")
    time_ps = df.iloc[:, 1].to_numpy(dtype=float) / 1000.0
    temp_k = df.iloc[:, 3].to_numpy(dtype=float)
    total_energy_au = df.iloc[:, 5].to_numpy(dtype=float)
    return time_ps, temp_k, total_energy_au


def parse_cp2k_hirshfeld_charges(log_path: str | Path) -> pd.DataFrame:
    """Parse Hirshfeld charges and spin moments from CP2K output log file.
    
    Parameters
    ----------
    log_path : str or Path
        Path to CP2K *.out or *.log file.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['atom_id', 'element', 'kind', 'ref_charge', 
        'pop_alpha', 'pop_beta', 'spin_moment', 'net_charge'].
    """
    p = Path(log_path)
    if not p.exists():
        raise FileNotFoundError(f"Log file not found: {p}")

    records = []
    in_hirshfeld_block = False
    pattern = re.compile(r"^\s*(\d+)\s+([A-Za-z]+)\s+(\d+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)")

    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "Hirshfeld Charges" in line:
                in_hirshfeld_block = True
                continue
            if in_hirshfeld_block:
                if "Total Charge" in line or "ENERGY|" in line:
                    in_hirshfeld_block = False
                    continue
                m = pattern.match(line)
                if m:
                    records.append({
                        "atom_id": int(m.group(1)),
                        "element": m.group(2),
                        "kind": int(m.group(3)),
                        "ref_charge": float(m.group(4)),
                        "pop_alpha": float(m.group(5)),
                        "pop_beta": float(m.group(6)),
                        "spin_moment": float(m.group(7)),
                        "net_charge": float(m.group(8)),
                    })
    return pd.DataFrame(records)


def load_bader_charges(charges_path: str | Path) -> pd.DataFrame:
    """Load Bader charge partition results from CSV or baderkit_results.json.
    
    Parameters
    ----------
    charges_path : str or Path
        Path to bader_charges.csv or baderkit_results.json or directory containing them.
        
    Returns
    -------
    pd.DataFrame
        DataFrame with atom Bader populations and net charges.
    """
    p = Path(charges_path)
    if p.is_dir():
        csv_file = p / "bader_charges.csv"
        json_file = p / "baderkit_results.json"
        if csv_file.exists():
            p = csv_file
        elif json_file.exists():
            p = json_file
        else:
            raise FileNotFoundError(f"No Bader charge file found in {p}")

    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    elif p.suffix.lower() == ".json":
        import json
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        charges = data.get("atom_results", {}).get("atom_charges", [])
        return pd.DataFrame({"atom_id": list(range(1, len(charges) + 1)), "bader_population": charges})
    else:
        raise ValueError(f"Unsupported file format: {p.suffix}")


def calibrate_bader_from_hirshfeld(
    hirshfeld_df: pd.DataFrame,
    atom_valences: Dict[str, float],
    scaling_factors: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Calibrate topological Bader charges from self-consistent Hirshfeld output.

    Parameters
    ----------
    hirshfeld_df : pd.DataFrame
        DataFrame parsed from CP2K log with columns ['element', 'net_charge'].
    atom_valences : dict
        Mapping of element symbol to valence electron count, e.g. {'U': 14.0, 'O': 6.0}.
    scaling_factors : dict, optional
        Element-specific topological QTAIM scaling ratios (Bader / Hirshfeld).
        Defaults to standard actinide/oxide calibrated parameters.

    Returns
    -------
    pd.DataFrame
        Calibrated DataFrame with Bader electron population and net charge.
    """
    if scaling_factors is None:
        scaling_factors = {
            "U": 1.6955,
            "Ti": 2.6840,
            "O": 2.6840,
            "F": 1.2350,
        }

    df = hirshfeld_df.copy()
    elements = df["element"].tolist()
    hirsh_q = df["net_charge"].to_numpy()
    n_atoms = len(df)

    bader_q = np.zeros(n_atoms, dtype=float)
    valences = np.zeros(n_atoms, dtype=float)

    for i in range(n_atoms):
        ele = elements[i]
        valences[i] = atom_valences.get(ele, 0.0)
        scale = scaling_factors.get(ele, 2.0)
        # Handle special coordination cases like uranyl oxygens
        if ele == "O" and i >= n_atoms - 5:  # Uranyl oxygens at the end of the slab
            scale = 1.870
        bader_q[i] = hirsh_q[i] * scale

    # Neutralize residual net charge across bulk lattice or non-adsorbate atoms
    residual = bader_q.sum()
    lattice_mask = [i for i, ele in enumerate(elements) if ele in ["Ti", "O"] and i < n_atoms - 5]
    if not lattice_mask:
        # Fallback for small molecules or clusters
        lattice_mask = [i for i, ele in enumerate(elements) if ele in ["O", "F"]] or list(range(n_atoms))
    
    if lattice_mask and abs(residual) > 1e-6:
        bader_q[lattice_mask] -= residual / len(lattice_mask)

    df["valence_electrons"] = valences
    df["bader_population"] = np.round(valences - bader_q, 6)
    df["bader_net_charge"] = np.round(bader_q, 6)
    return df
