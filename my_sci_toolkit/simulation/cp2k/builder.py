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



    def build_finite_system(
        self,
        atoms: List[Tuple[str, float, float, float]],
        cell: Dict[str, float],
        *,
        kind_definitions: Dict[str, Dict[str, Any]],
        total_charge: Optional[int] = None,
        multiplicity: Optional[int] = None,
        uks: Optional[bool] = None,
        cell_periodicity: str = "NONE",
        poisson_periodicity: str = "NONE",
        poisson_solver: str = "MT",
        center_coordinates: bool = False,
        basis_file_name: str = "BASIS_MOLOPT",
        potential_file_name: str = "GTH_POTENTIALS",
        xc_functional: Optional[str] = None,
        dispersion_model: Optional[str] = None,
        dispersion_reference_functional: Optional[str] = None,
        dispersion_parameter_file: Optional[str] = None,
        cutoff_ry: Optional[float] = None,
        rel_cutoff_ry: Optional[float] = None,
        run_type: Optional[str] = None,
        scf_method: str = "OT",
        eps_scf: float = 1.0e-6,
        max_scf: int = 100,
        smearing: Optional[Dict[str, Any]] = None,
        added_mos: Optional[int] = None,
        mixing: Optional[Dict[str, Any]] = None,
        print_sections: Optional[List[str]] = None,
    ) -> str:
        """Build a user-configured finite/cluster CP2K input without changing legacy defaults.

        The atom tuple's first value is the CP2K KIND label. Distinct labels may map
        to the same element but use different basis or pseudopotential definitions.
        """
        import math

        if not atoms:
            raise ValueError("finite-system builder requires at least one atom")
        allowed_periodicity = {"NONE", "X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"}
        cell_periodicity = str(cell_periodicity).upper()
        poisson_periodicity = str(poisson_periodicity).upper()
        if cell_periodicity not in allowed_periodicity or poisson_periodicity not in allowed_periodicity:
            raise ValueError("unsupported cell or Poisson periodicity")
        if cell_periodicity == "NONE" and poisson_periodicity != "NONE":
            raise ValueError("non-periodic cells require non-periodic Poisson boundary conditions")
        solver = str(poisson_solver).upper()
        if solver not in {"MT", "WAVELET", "ANALYTIC"}:
            raise ValueError("poisson_solver must be MT, WAVELET or ANALYTIC")
        task = str(run_type or self.run_type).upper()
        if task not in {"ENERGY", "ENERGY_FORCE", "GEO_OPT"}:
            raise ValueError("run_type must be ENERGY, ENERGY_FORCE or GEO_OPT")
        method = str(scf_method).upper()
        if method not in {"OT", "DIAGONALIZATION"}:
            raise ValueError("scf_method must be OT or DIAGONALIZATION")
        if smearing and method != "DIAGONALIZATION":
            raise ValueError("smearing requires DIAGONALIZATION; OT and smearing are not combined")
        if not math.isfinite(float(eps_scf)) or eps_scf <= 0 or int(max_scf) < 1:
            raise ValueError("eps_scf and max_scf must be positive")
        if not basis_file_name or not potential_file_name:
            raise ValueError("basis_file_name and potential_file_name are required")

        labels = [str(atom[0]) for atom in atoms]
        required_labels = set(labels)
        if set(kind_definitions) != required_labels:
            missing = sorted(required_labels - set(kind_definitions))
            extra = sorted(set(kind_definitions) - required_labels)
            raise ValueError(f"KIND definitions must exactly match coordinate labels; missing={missing}, extra={extra}")
        for label in required_labels:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_+-]*", label):
                raise ValueError(f"invalid CP2K KIND label: {label!r}")
            for key in ("element", "basis_set", "potential"):
                if not kind_definitions[label].get(key):
                    raise ValueError(f"KIND {label!r} requires {key}")

        xyz = [[float(v) for v in atom[1:4]] for atom in atoms]
        if not all(math.isfinite(v) for row in xyz for v in row):
            raise ValueError("all coordinates must be finite")
        lengths = [float(cell.get(axis, 0.0)) for axis in ("a", "b", "c")]
        if not all(math.isfinite(v) and v > 0 for v in lengths):
            raise ValueError("cell requires positive finite a, b and c lengths")
        angles = [float(cell.get(axis, 90.0)) for axis in ("alpha", "beta", "gamma")]
        if not all(math.isfinite(v) and 0 < v < 180 for v in angles):
            raise ValueError("cell angles must lie between 0 and 180 degrees")
        if center_coordinates:
            centroid = [sum(row[i] for row in xyz) / len(xyz) for i in range(3)]
            shift = [lengths[i] / 2.0 - centroid[i] for i in range(3)]
            xyz = [[row[i] + shift[i] for i in range(3)] for row in xyz]

        charge = self.config.charge if total_charge is None else int(total_charge)
        mult = self.config.multiplicity if multiplicity is None else int(multiplicity)
        if mult < 1:
            raise ValueError("multiplicity must be >= 1")
        spin_polarized = (mult > 1) if uks is None else bool(uks)
        if mult > 1 and not spin_polarized:
            raise ValueError("multiplicity > 1 requires UKS")
        has_valence = all("valence_electrons" in kind_definitions[label] for label in required_labels)
        if has_valence:
            electron_count = sum(
                float(kind_definitions[label]["valence_electrons"]) *
                labels.count(label) for label in required_labels
            ) - charge
            if not math.isfinite(electron_count) or electron_count <= 0 or not math.isclose(
                electron_count, round(electron_count), abs_tol=1.0e-8
            ):
                raise ValueError("valence electron count minus charge must be a positive integer")
            if (int(round(electron_count)) - (mult - 1)) % 2 != 0:
                raise ValueError("electron-count / multiplicity parity is inconsistent")
        elif mult > 1:
            raise ValueError("valence_electrons is required for every KIND for open-shell parity validation")

        functional = str(xc_functional or self.functional).upper()
        cutoff = float(self.cutoff_ry if cutoff_ry is None else cutoff_ry)
        rel_cutoff = float(self.rel_cutoff_ry if rel_cutoff_ry is None else rel_cutoff_ry)
        if cutoff <= 0 or rel_cutoff <= 0 or not math.isfinite(cutoff + rel_cutoff):
            raise ValueError("cutoff_ry and rel_cutoff_ry must be positive and finite")

        lines = [
            "&GLOBAL", f"  PROJECT {self.project_name}", f"  RUN_TYPE {task}",
            "  PRINT_LEVEL LOW", "&END GLOBAL", "",
            "&FORCE_EVAL", "  METHOD Quickstep", "  &DFT",
            f"    BASIS_SET_FILE_NAME {basis_file_name}",
            f"    POTENTIAL_FILE_NAME {potential_file_name}",
            f"    CHARGE {charge}", f"    MULTIPLICITY {mult}",
        ]
        if spin_polarized:
            lines.append("    UKS TRUE")
        lines += [
            "    &MGRID", f"      CUTOFF {cutoff:g}", f"      REL_CUTOFF {rel_cutoff:g}", "    &END MGRID",
            "    &POISSON", f"      PERIODIC {poisson_periodicity}", f"      PSOLVER {solver}", "    &END POISSON",
            "    &SCF", "      SCF_GUESS ATOMIC", f"      EPS_SCF {float(eps_scf):.8g}",
            f"      MAX_SCF {int(max_scf)}",
        ]
        if method == "OT":
            lines += ["      &OT", "        MINIMIZER DIIS", "        PRECONDITIONER FULL_SINGLE_INVERSE", "      &END OT"]
        else:
            lines += ["      &DIAGONALIZATION", "      &END DIAGONALIZATION"]
        if smearing:
            smear_method = str(smearing.get("method", "FERMI_DIRAC")).upper()
            temperature = float(smearing.get("temperature_k", 0.0))
            if not math.isfinite(temperature) or temperature <= 0:
                raise ValueError("smearing.temperature_k must be positive and finite")
            lines += [
                "      &SMEAR", f"        METHOD {smear_method}",
                f"        ELECTRONIC_TEMPERATURE [K] {temperature:g}", "      &END SMEAR",
            ]
        if added_mos is not None:
            if int(added_mos) < 0:
                raise ValueError("added_mos cannot be negative")
            lines.append(f"      ADDED_MOS {int(added_mos)}")
        if mixing:
            mix_method = str(mixing.get("method", "BROYDEN_MIXING")).upper()
            alpha = float(mixing.get("alpha", 0.4))
            buffer = int(mixing.get("n_buffer", 5))
            if not math.isfinite(alpha) or not 0 < alpha <= 1 or buffer < 1:
                raise ValueError("mixing alpha must be in (0, 1] and n_buffer positive")
            lines += [
                "      &MIXING", f"        METHOD {mix_method}",
                f"        ALPHA {alpha:g}", f"        NBUFFER {buffer}", "      &END MIXING",
            ]
        lines += [
            "    &END SCF", "    &XC", "      &XC_FUNCTIONAL",
            f"        &{functional}", f"        &END {functional}", "      &END XC_FUNCTIONAL",
        ]
        if dispersion_model:
            lines += ["      &VDW_POTENTIAL", "        POTENTIAL_TYPE PAIR_POTENTIAL",
                      "        &PAIR_POTENTIAL", f"          TYPE {str(dispersion_model).upper()}"]
            if dispersion_parameter_file:
                lines.append(f"          PARAMETER_FILE_NAME {dispersion_parameter_file}")
            if dispersion_reference_functional:
                lines.append(f"          REFERENCE_FUNCTIONAL {dispersion_reference_functional}")
            lines += ["        &END PAIR_POTENTIAL", "      &END VDW_POTENTIAL"]
        allowed_print = {"MO_CUBES", "E_DENSITY_CUBE", "V_HARTREE_CUBE", "PDOS", "HIRSHFELD", "MULLIKEN"}
        if print_sections:
            lines += ["      &PRINT"]
            for section in print_sections:
                name = str(section).upper()
                if name not in allowed_print:
                    raise ValueError(f"unsupported print section: {section}")
                lines += [f"        &{name}", f"        &END {name}"]
            lines.append("      &END PRINT")
        lines += [
            "    &END XC", "  &END DFT", "  &SUBSYS", "    &CELL",
            f"      ABC {lengths[0]:.8f} {lengths[1]:.8f} {lengths[2]:.8f}",
            f"      ALPHA_BETA_GAMMA {angles[0]:g} {angles[1]:g} {angles[2]:g}",
            f"      PERIODIC {cell_periodicity}", "    &END CELL", "    &COORD",
        ]
        for (label, _, _, _), row in zip(atoms, xyz):
            lines.append(f"      {label:<12s} {row[0]:.10f} {row[1]:.10f} {row[2]:.10f}")
        lines.append("    &END COORD")
        for label in sorted(required_labels):
            definition = kind_definitions[label]
            lines += [
                f"    &KIND {label}", f"      ELEMENT {definition['element']}",
                f"      BASIS_SET {definition['basis_set']}", f"      POTENTIAL {definition['potential']}",
                "    &END KIND",
            ]
        lines += ["  &END SUBSYS", "&END FORCE_EVAL"]
        if task == "GEO_OPT":
            lines += ["", "&MOTION", "  &GEO_OPT", "    OPTIMIZER BFGS", "  &END GEO_OPT", "&END MOTION"]
        return "\n".join(lines) + "\n"

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
