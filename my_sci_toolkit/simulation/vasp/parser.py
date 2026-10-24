"""VASP calculation log and electronic structure parsers (OUTCAR, OSZICAR)."""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from my_sci_toolkit.simulation.base import BaseParser


class VASPParser(BaseParser):
    """Parser for VASP calculation files (OUTCAR, OSZICAR)."""

    def get_final_energy(self) -> Optional[float]:
        """Extract free energy TOTEN (eV) from OUTCAR or OSZICAR."""
        energy = None
        # Try OSZICAR or OUTCAR
        if self.log_path.name.upper() == "OSZICAR" or "OSZICAR" in str(self.log_path):
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if "F=" in line and "E0=" in line:
                        parts = line.split()
                        for i, p in enumerate(parts):
                            if p == "F=":
                                energy = float(parts[i + 1])
        else:
            pattern = re.compile(r"free  energy   TOTEN  =\s+([-\d\.]+)\s+eV")
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = pattern.search(line)
                    if m:
                        energy = float(m.group(1))
        return energy

    def is_converged(self) -> bool:
        """Check whether electronic and ionic steps reached convergence."""
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return "reached required accuracy" in content

    def parse_ionic_energies(self) -> List[float]:
        """Extract energy trajectory for each ionic relaxation step from OSZICAR."""
        energies = []
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if "F=" in line and "E0=" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "F=":
                            energies.append(float(parts[i + 1]))
        return energies
