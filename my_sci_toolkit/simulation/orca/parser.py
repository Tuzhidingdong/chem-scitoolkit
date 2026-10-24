"""ORCA calculation log, vibrational frequency, and electronic state parsers."""

import re
from pathlib import Path
from typing import Optional, List, Tuple
from my_sci_toolkit.simulation.base import BaseParser


class ORCAParser(BaseParser):
    """Parser for ORCA standard calculation logs (*.out)."""

    def get_final_energy(self) -> Optional[float]:
        """Extract final single point or optimized energy in Hartree."""
        energy = None
        pattern = re.compile(r"FINAL SINGLE POINT ENERGY\s+([-\d\.]+)")
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    energy = float(m.group(1))
        return energy

    def is_converged(self) -> bool:
        """Check whether geometry optimization and SCF converged."""
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return "OPTIMIZATION RUN DONE" in content or "SUCCESSFULLY CONVERGED" in content

    def parse_vibrational_frequencies(self) -> List[Tuple[float, float]]:
        """Extract harmonic vibrational frequencies (cm^-1) and IR intensities (km/mol)."""
        freqs = []
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        in_ir_spectrum = False
        for line in lines:
            if "IR SPECTRUM" in line:
                in_ir_spectrum = True
                continue
            if in_ir_spectrum:
                if "The first frequency" in line or "-------" in line or not line.strip():
                    continue
                parts = line.split()
                # Format: Mode  Freq (cm**-1)  T**2  TX  TY  TZ
                if len(parts) >= 3 and parts[0].replace(":", "").isdigit():
                    try:
                        freq = float(parts[1])
                        inten = float(parts[2])
                        freqs.append((freq, inten))
                    except ValueError:
                        pass
                elif "THERMOCHEMISTRY" in line:
                    break

        return freqs
