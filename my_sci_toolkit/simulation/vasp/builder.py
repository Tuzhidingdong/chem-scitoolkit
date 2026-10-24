"""VASP input file generator (INCAR, KPOINTS, POSCAR, POTCAR)."""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from my_sci_toolkit.simulation.base import BaseInputBuilder


class VASPInputBuilder(BaseInputBuilder):
    """VASP input card generator refactored from cp2kMD.py (Incar_kpoints, Poscar)."""

    def __init__(
        self,
        incar_params: Optional[Dict[str, Any]] = None,
        kpoints_mesh: Tuple[int, int, int] = (3, 3, 1),
    ):
        super().__init__()
        default_incar = {
            "SYSTEM": "VASP_Calculation",
            "ENCUT": 500,
            "EDIFF": 1E-6,
            "EDIFFG": -0.02,
            "ISMEAR": 0,
            "SIGMA": 0.05,
            "IBRION": 2,
            "NSW": 100,
            "LREAL": "Auto",
            "LWAVE": ".FALSE.",
            "LCHARG": ".FALSE.",
        }
        if incar_params:
            default_incar.update(incar_params)
        self.incar_params = default_incar
        self.kpoints_mesh = kpoints_mesh

    def build_incar(self) -> str:
        """Construct INCAR content."""
        lines = []
        for k, v in self.incar_params.items():
            lines.append(f"  {k:<12s} = {v}")
        return "\n".join(lines)

    def build_kpoints(self, comment: str = "Gamma-centered Monkhorst-Pack") -> str:
        """Construct standard Monkhorst-Pack KPOINTS file."""
        lines = [
            comment,
            "0",
            "Monkhorst-Pack",
            f"  {self.kpoints_mesh[0]} {self.kpoints_mesh[1]} {self.kpoints_mesh[2]}",
            "  0 0 0"
        ]
        return "\n".join(lines)

    def build_poscar_from_atoms(
        self,
        comment: str,
        lattice: List[List[float]],
        element_counts: Dict[str, int],
        coords: List[List[float]],
        selective_dynamics: bool = False,
        freeze_flags: Optional[List[Tuple[bool, bool, bool]]] = None,
    ) -> str:
        """Build standard POSCAR file text."""
        lines = [comment, "1.0"]
        for row in lattice:
            lines.append(f"  {row[0]:>12.6f} {row[1]:>12.6f} {row[2]:>12.6f}")

        elements = list(element_counts.keys())
        counts = [str(element_counts[e]) for e in elements]
        lines.append("  " + "  ".join(elements))
        lines.append("  " + "  ".join(counts))

        if selective_dynamics:
            lines.append("Selective dynamics")
        lines.append("Direct")

        for idx, pos in enumerate(coords):
            line = f"  {pos[0]:>12.6f} {pos[1]:>12.6f} {pos[2]:>12.6f}"
            if selective_dynamics:
                flags = freeze_flags[idx] if freeze_flags and idx < len(freeze_flags) else (True, True, True)
                f_str = f" {'T' if flags[0] else 'F'} {'T' if flags[1] else 'F'} {'T' if flags[2] else 'F'}"
                line += f_str
            lines.append(line)

        return "\n".join(lines)

    def build(self, **kwargs) -> str:
        return self.build_incar()


def write_vasp_inputs(
    output_dir: str | Path,
    incar_params: Optional[Dict[str, Any]] = None,
    kpoints_mesh: Tuple[int, int, int] = (3, 3, 1),
) -> Dict[str, Path]:
    """Convenience helper to generate INCAR and KPOINTS in target directory."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    builder = VASPInputBuilder(incar_params, kpoints_mesh)

    incar_path = out_dir / "INCAR"
    kpoints_path = out_dir / "KPOINTS"

    with open(incar_path, "w", encoding="utf-8") as f:
        f.write(builder.build_incar())

    with open(kpoints_path, "w", encoding="utf-8") as f:
        f.write(builder.build_kpoints())

    return {"INCAR": incar_path, "KPOINTS": kpoints_path}
