"""CP2K input file generator from CIF crystal structure and molecular geometries."""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from my_sci_toolkit.simulation.base import BaseInputBuilder, CalculationConfig
from my_sci_toolkit.registry import tool


def parse_cif_basic(cif_path: str | Path) -> Tuple[Dict[str, float], List[Tuple[str, float, float, float]]]:
    """Parse lattice parameters and atomic fractional or cartesian coordinates from a CIF file.

    Fallback parser that works without requiring heavy dependencies like pymatgen.
    """
    p = Path(cif_path)
    if not p.exists():
        raise FileNotFoundError(f"CIF file not found: {p}")

    with open(p, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Extract lattice lengths and angles
    def get_val(pattern: str, default: float) -> float:
        m = re.search(pattern, text)
        if m:
            clean = re.sub(r"\(.*?\)", "", m.group(1)).strip()
            try:
                return float(clean)
            except ValueError:
                pass
        return default

    cell = {
        "a": get_val(r"_cell_length_a\s+([\d\.]+)", 10.0),
        "b": get_val(r"_cell_length_b\s+([\d\.]+)", 10.0),
        "c": get_val(r"_cell_length_c\s+([\d\.]+)", 10.0),
        "alpha": get_val(r"_cell_angle_alpha\s+([\d\.]+)", 90.0),
        "beta": get_val(r"_cell_angle_beta\s+([\d\.]+)", 90.0),
        "gamma": get_val(r"_cell_angle_gamma\s+([\d\.]+)", 90.0),
    }

    # Extract atoms: _atom_site_type_symbol ... _atom_site_fract_x/y/z
    atoms: List[Tuple[str, float, float, float]] = []
    lines = text.splitlines()
    in_atom_loop = False
    headers = []

    for line in lines:
        sline = line.strip()
        if sline.startswith("_atom_site_"):
            in_atom_loop = True
            headers.append(sline)
            continue
        if in_atom_loop:
            if sline.startswith("loop_") or (sline.startswith("_") and not sline.startswith("_atom_site_")):
                in_atom_loop = False
                headers = []
                continue
            parts = sline.split()
            if len(parts) >= 4 and not sline.startswith("#"):
                # Clean coordinates of error parentheses
                try:
                    elem = re.sub(r"[^A-Za-z]", "", parts[0])
                    x_idx = [i for i, h in enumerate(headers) if "fract_x" in h or "Cartn_x" in h]
                    y_idx = [i for i, h in enumerate(headers) if "fract_y" in h or "Cartn_y" in h]
                    z_idx = [i for i, h in enumerate(headers) if "fract_z" in h or "Cartn_z" in h]

                    idx_x = x_idx[0] if x_idx else 1
                    idx_y = y_idx[0] if y_idx else 2
                    idx_z = z_idx[0] if z_idx else 3

                    x = float(re.sub(r"\(.*?\)", "", parts[idx_x]))
                    y = float(re.sub(r"\(.*?\)", "", parts[idx_y]))
                    z = float(re.sub(r"\(.*?\)", "", parts[idx_z]))
                    # Convert fractional to approximate cartesian for orthorhombic/cubic
                    x_cart = x * cell["a"]
                    y_cart = y * cell["b"]
                    z_cart = z * cell["c"]
                    atoms.append((elem, x_cart, y_cart, z_cart))
                except (ValueError, IndexError):
                    continue

    return cell, atoms


class CP2KInputBuilder(BaseInputBuilder):
    """Modular CP2K input file builder refactored from cp2kMD.py (frame and dftgenerate)."""

    def __init__(
        self,
        project_name: str = "aimd",
        run_type: str = "GEO_OPT",  # ENERGY, GEO_OPT, MD, CELL_OPT
        functional: str = "PBE",
        cutoff_ry: int = 400,
        rel_cutoff_ry: int = 50,
        ot_method: bool = True,
        temperature_k: float = 300.0,
        timestep_fs: float = 0.5,
        periodic: str = "XYZ",
    ):
        super().__init__()
        self.project_name = project_name
        self.run_type = run_type
        self.functional = functional.upper()
        self.cutoff_ry = cutoff_ry
        self.rel_cutoff_ry = rel_cutoff_ry
        self.ot_method = ot_method
        self.temperature_k = temperature_k
        self.timestep_fs = timestep_fs
        self.periodic = periodic

    def build_from_structure(
        self,
        cell_dict: Dict[str, float],
        atoms: List[Tuple[str, float, float, float]],
        colvar_block: Optional[str] = None,
    ) -> str:
        """Construct full CP2K input text from cell dimensions and atomic coordinates."""
        lines: List[str] = []

        # GLOBAL block
        lines.append("&GLOBAL")
        lines.append(f"  PROJECT {self.project_name}")
        lines.append(f"  RUN_TYPE {self.run_type}")
        lines.append("  PRINT_LEVEL LOW")
        lines.append("&END GLOBAL")
        lines.append("")

        # FORCE_EVAL
        lines.append("&FORCE_EVAL")
        lines.append("  METHOD Quickstep")
        lines.append("  &DFT")
        lines.append("    BASIS_SET_FILE_NAME BASIS_MOLOPT")
        lines.append("    POTENTIAL_FILE_NAME GTH_POTENTIALS")
        lines.append(f"    CHARGE {self.config.charge}")
        lines.append(f"    MULTIPLICITY {self.config.multiplicity}")
        lines.append("    &MGRID")
        lines.append(f"      CUTOFF {self.cutoff_ry}")
        lines.append(f"      REL_CUTOFF {self.rel_cutoff_ry}")
        lines.append("    &END MGRID")
        lines.append("    &QS")
        lines.append("      EPS_DEFAULT 1.0E-12")
        lines.append("    &END QS")
        lines.append("    &SCF")
        lines.append("      SCF_GUESS ATOMIC")
        lines.append("      EPS_SCF 1.0E-6")
        lines.append("      MAX_SCF 60")
        if self.ot_method:
            lines.append("      &OT ON")
            lines.append("        MINIMIZER DIIS")
            lines.append("        PRECONDITIONER FULL_ALL")
            lines.append("        ENERGY_GAP 0.001")
            lines.append("      &END OT")
            lines.append("      &OUTER_SCF")
            lines.append("        EPS_SCF 1.0E-6")
            lines.append("        MAX_SCF 10")
            lines.append("      &END OUTER_SCF")
        lines.append("    &END SCF")
        lines.append("    &XC")
        lines.append("      &XC_FUNCTIONAL")
        lines.append(f"        &{self.functional}")
        lines.append(f"        &END {self.functional}")
        lines.append("      &END XC_FUNCTIONAL")
        lines.append("      &VDW_POTENTIAL")
        lines.append("        POTENTIAL_TYPE PAIR_POTENTIAL")
        lines.append("        &PAIR_POTENTIAL")
        lines.append("          TYPE DFTD3")
        lines.append("          PARAMETER_FILE_NAME dftd3.dat")
        lines.append("          REFERENCE_FUNCTIONAL PBE")
        lines.append("        &END PAIR_POTENTIAL")
        lines.append("      &END VDW_POTENTIAL")
        lines.append("    &END XC")
        lines.append("  &END DFT")
        lines.append("")

        # SUBSYS (Cell & Coords)
        lines.append("  &SUBSYS")
        lines.append("    &CELL")
        lines.append(f"      ABC {cell_dict.get('a', 15.0):.4f} {cell_dict.get('b', 15.0):.4f} {cell_dict.get('c', 15.0):.4f}")
        lines.append(f"      ALPHA_BETA_GAMMA {cell_dict.get('alpha', 90.0):.2f} {cell_dict.get('beta', 90.0):.2f} {cell_dict.get('gamma', 90.0):.2f}")
        lines.append(f"      PERIODIC {self.periodic}")
        lines.append("    &END CELL")
        lines.append("    &COORD")
        for elem, x, y, z in atoms:
            lines.append(f"      {elem:<4s} {x:>12.6f} {y:>12.6f} {z:>12.6f}")
        lines.append("    &END COORD")

        # Set default potentials and basis sets per element
        unique_elems = sorted(list(set([elem for elem, _, _, _ in atoms])))
        for elem in unique_elems:
            lines.append(f"    &KIND {elem}")
            lines.append(f"      BASIS_SET DZVP-MOLOPT-SR-GTH")
            lines.append(f"      POTENTIAL GTH-PBE")
            lines.append(f"    &END KIND")

        if colvar_block:
            lines.append(colvar_block)

        lines.append("  &END SUBSYS")
        lines.append("&END FORCE_EVAL")

        # MOTION (if MD or GEO_OPT)
        if self.run_type == "MD":
            lines.append("")
            lines.append("&MOTION")
            lines.append("  &MD")
            lines.append("    ENSEMBLE NVT")
            lines.append(f"    TEMPERATURE [K] {self.temperature_k}")
            lines.append(f"    TIMESTEP [fs] {self.timestep_fs}")
            lines.append("    STEPS 20000")
            lines.append("    &THERMOSTAT")
            lines.append("      TYPE CSVR")
            lines.append("      &CSVR")
            lines.append("        TIMECON [fs] 20.0")
            lines.append("      &END CSVR")
            lines.append("    &END THERMOSTAT")
            lines.append("  &END MD")
            lines.append("&END MOTION")

        return "\n".join(lines)

    def build(self, **kwargs) -> str:
        cif_path = kwargs.get("cif_path")
        if not cif_path:
            raise ValueError("cif_path parameter is required to build CP2K input.")
        cell, atoms = parse_cif_basic(cif_path)
        colvar_block = kwargs.get("colvar_block")
        return self.build_from_structure(cell, atoms, colvar_block=colvar_block)


@tool(
    name="build_cp2k_from_cif",
    description="Convenient top-level builder: Read a crystal CIF file and generate a production-ready CP2K input file.",
    tags=["simulation", "cp2k"]
)
def build_cp2k_from_cif(
    cif_path: str | Path,
    output_inp: str | Path = "cp2k.inp",
    run_type: str = "GEO_OPT",
    functional: str = "PBE",
    cutoff_ry: int = 400,
    project_name: str = "aimd",
) -> Path:
    """Read a CIF file and output a full CP2K input card (cp2k.inp).

    Refactored from cp2kMD.py (frame and dftgenerate).
    """
    builder = CP2KInputBuilder(
        project_name=project_name,
        run_type=run_type,
        functional=functional,
        cutoff_ry=cutoff_ry,
    )
    return builder.write(output_inp, cif_path=cif_path)
