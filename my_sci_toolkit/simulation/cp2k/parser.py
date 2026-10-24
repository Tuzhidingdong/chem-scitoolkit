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
