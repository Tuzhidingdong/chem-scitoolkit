"""ORCA quantum chemistry input file generator."""

from pathlib import Path
from typing import List, Tuple, Optional
from my_sci_toolkit.simulation.base import BaseInputBuilder


class ORCAInputBuilder(BaseInputBuilder):
    """ORCA calculation input generator refactored from cp2kMD.py (ORCA, TDADFTgen)."""

    def __init__(
        self,
        method: str = "B3LYP",
        basis: str = "def2-SVP",
        task: str = "Opt Freq",  # SP, Opt, Opt Freq
        dispersion: str = "D3BJ",
        solvent: Optional[str] = "CPCM(Water)",
        nprocs: int = 16,
        maxcore_mb: int = 4000,
        charge: int = 0,
        multiplicity: int = 1,
    ):
        super().__init__()
        self.method = method
        self.basis = basis
        self.task = task
        self.dispersion = dispersion
        self.solvent = solvent
        self.nprocs = nprocs
        self.maxcore_mb = maxcore_mb
        self.charge = charge
        self.multiplicity = multiplicity

    def build_from_coordinates(self, atoms: List[Tuple[str, float, float, float]]) -> str:
        """Generate standard ORCA .inp string from atomic positions."""
        lines = []

        # Simple route line
        route = f"! {self.method} {self.basis} {self.task}"
        if self.dispersion:
            route += f" {self.dispersion}"
        if self.solvent:
            route += f" {self.solvent}"
        lines.append(route)
        lines.append("")

        # Resource blocks
        lines.append(f"%maxcore {self.maxcore_mb}")
        lines.append(f"%pal nprocs {self.nprocs} end")
        lines.append("")

        # Coordinates block
        lines.append(f"* xyz {self.charge} {self.multiplicity}")
        for elem, x, y, z in atoms:
            lines.append(f"  {elem:<4s} {x:>12.6f} {y:>12.6f} {z:>12.6f}")
        lines.append("*")

        return "\n".join(lines)

    def build(self, **kwargs) -> str:
        atoms = kwargs.get("atoms", [])
        return self.build_from_coordinates(atoms)


def write_orca_input(
    output_path: str | Path,
    atoms: List[Tuple[str, float, float, float]],
    method: str = "B3LYP",
    basis: str = "def2-SVP",
    task: str = "Opt Freq",
    charge: int = 0,
    multiplicity: int = 1,
) -> Path:
    """Convenience builder to output a clean ORCA input card."""
    builder = ORCAInputBuilder(
        method=method,
        basis=basis,
        task=task,
        charge=charge,
        multiplicity=multiplicity,
    )
    return builder.write(output_path, atoms=atoms)
