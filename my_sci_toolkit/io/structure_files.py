"""Molecular and crystal structure format conversion helpers."""

from pathlib import Path
from typing import List, Dict, Tuple


def pdb_to_xyz(input_pdb: str | Path, output_xyz: str | Path) -> Path:
    """Convert a standard PDB coordinate file to extended XYZ trajectory format."""
    in_p = Path(input_pdb)
    out_p = Path(output_xyz)
    if not in_p.exists():
        raise FileNotFoundError(f"PDB file not found: {in_p}")

    atoms: List[Tuple[str, float, float, float]] = []
    with open(in_p, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                element = line[76:78].strip()
                if not element:
                    element = line[12:16].strip()
                    element = ''.join([c for c in element if not c.isdigit()])
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                atoms.append((element, x, y, z))

    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        f.write(f"{len(atoms)}\n")
        f.write(f"Converted from {in_p.name}\n")
        for elem, x, y, z in atoms:
            f.write(f"{elem:<4} {x:>12.6f} {y:>12.6f} {z:>12.6f}\n")

    return out_p


def xyz_to_pdb(input_xyz: str | Path, output_pdb: str | Path) -> Path:
    """Convert an XYZ structure into standard PDB format."""
    in_p = Path(input_xyz)
    out_p = Path(output_pdb)
    if not in_p.exists():
        raise FileNotFoundError(f"XYZ file not found: {in_p}")

    with open(in_p, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    atom_count = int(lines[0])
    coord_lines = lines[2:2 + atom_count]

    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        for idx, line in enumerate(coord_lines, 1):
            parts = line.split()
            elem = parts[0]
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            f.write(
                f"ATOM  {idx:>5d} {elem:<4s} MOL A   1    {x:>8.3f}{y:>8.3f}{z:>8.3f}  1.00  0.00          {elem:>2s}\n"
            )
        f.write("END\n")

    return out_p
