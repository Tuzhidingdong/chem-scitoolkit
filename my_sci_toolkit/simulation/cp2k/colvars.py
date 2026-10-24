"""CP2K collective variables (COLVAR) and metadynamics restraint generator."""

from typing import List, Optional, Dict, Any


def generate_distance_colvar(atom_a: int, atom_b: int, colvar_id: int = 1) -> str:
    """Generate CP2K &COLVAR block for atomic distance."""
    lines = [
        f"    &COLVAR",
        f"      &DISTANCE",
        f"        ATOMS {atom_a} {atom_b}",
        f"      &END DISTANCE",
        f"    &END COLVAR"
    ]
    return "\n".join(lines)


def generate_coordination_colvar(
    species_a: List[int],
    species_b: List[int],
    r0_angstrom: float = 2.5,
    nn: int = 6,
    nd: int = 12,
    colvar_id: int = 1,
) -> str:
    """Generate CP2K &COLVAR block for coordination number."""
    lines = [
        "    &COLVAR",
        "      &COORDINATION",
        f"        R0 [angstrom] {r0_angstrom}",
        f"        NN {nn}",
        f"        ND {nd}",
        f"        ATOMS_FROM {' '.join(map(str, species_a))}",
        f"        ATOMS_TO {' '.join(map(str, species_b))}",
        "      &END COORDINATION",
        "    &END COLVAR"
    ]
    return "\n".join(lines)


def generate_metadynamics_free_energy_block(
    hills_height_kj_mol: float = 2.5,
    hills_sigma: float = 0.05,
    pace_steps: int = 50,
    well_tempered_temp_k: Optional[float] = 300.0,
    delta_t_k: Optional[float] = 1500.0,
) -> str:
    """Generate CP2K &FREE_ENERGY block for metadynamics (HILLS deposition)."""
    lines = [
        "&FREE_ENERGY",
        "  &METADYN",
        "    USE_PLUMED .FALSE.",
        f"    PACE {pace_steps}",
        f"    SCALE [kjmol] {hills_height_kj_mol}",
        f"    WIDTH [angstrom] {hills_sigma}",
    ]
    if well_tempered_temp_k and delta_t_k:
        lines.append(f"    WT_TEMPERATURE [K] {delta_t_k}")
        lines.append(f"    TEMP [K] {well_tempered_temp_k}")
    lines.append("  &END METADYN")
    lines.append("&END FREE_ENERGY")
    return "\n".join(lines)
