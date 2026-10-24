"""Crystal Orbital Hamilton Population (COHP) and Local Density of States (LDOS) via Multiwfn."""

from pathlib import Path
from typing import Dict, Any, Optional
from my_sci_toolkit.simulation.multiwfn.runner import MultiwfnRunner


def calculate_cohp_fragments(
    wfn_file: str | Path,
    fragment_1: str = "e Fe",
    fragment_2: str = "e Te",
    energy_range: str = "-12,4,2",
    multiwfn_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Calculate Crystal Orbital Hamilton Population (COHP) between two defined fragments.

    Refactored from cp2kMD.COHP_Multiwfn.
    """
    runner = MultiwfnRunner(multiwfn_path)
    # Menu sequence for COOP/COHP in Multiwfn: 100 -> 8
    commands = [
        "100",  # Other functions (Part 2)
        "8",    # Calculate COOP / COHP / IBSI
        "1",    # Specify Fragment 1
        fragment_1,
        "2",    # Specify Fragment 2
        fragment_2,
        "3",    # Set energy range
        energy_range,
        "-1",   # Plot COHP curve
        "0",    # Export data
    ]
    return runner.run_commands(input_file=wfn_file, commands=commands)


def calculate_ldos_atom(
    molden_file: str | Path,
    atom_index: int,
    multiwfn_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Calculate Local Density of States (LDOS) for a specific atomic center.

    Refactored from cp2kMD.ldos_Multiwfn.
    """
    runner = MultiwfnRunner(multiwfn_path)
    # Menu: 10 -> 2 (LDOS/PDOS)
    commands = [
        "10",               # Density of states
        "2",                # Calculate PDOS / LDOS
        "1",                # Define atom components
        str(atom_index),
        "-1",               # Draw curve and export table
    ]
    return runner.run_commands(input_file=molden_file, commands=commands)
