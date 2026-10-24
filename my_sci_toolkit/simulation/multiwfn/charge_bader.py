"""Bader charge, ESP electrostatic potential, and ELF analysis via Multiwfn."""

from pathlib import Path
from typing import Dict, Any, Optional
from my_sci_toolkit.simulation.multiwfn.runner import MultiwfnRunner


def run_bader_charge_analysis(
    cube_file: str | Path,
    multiwfn_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Automate Bader charge partitioning via Multiwfn."""
    runner = MultiwfnRunner(multiwfn_path)
    # Menu commands for Bader analysis: 17 -> 1
    commands = [
        "17",  # Basin analysis
        "1",   # Generate basins with default settings
        "2",   # Integrate electron density
        "0",   # Return
    ]
    return runner.run_commands(input_file=cube_file, commands=commands)


def run_esp_surface_analysis(
    wfn_or_fchk: str | Path,
    multiwfn_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Automate electrostatic potential (ESP) mapped on vdW surface."""
    runner = MultiwfnRunner(multiwfn_path)
    # Menu commands for quantitative molecular surface analysis: 12 -> 0
    commands = [
        "12",  # Quantitative surface analysis
        "0",   # Start analysis with default 0.001 a.u. isodensity
    ]
    return runner.run_commands(input_file=wfn_or_fchk, commands=commands)


def generate_elf_grid(
    fchk_file: str | Path,
    grid_quality: int = 2,  # 1: Low, 2: Medium, 3: High
    multiwfn_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Generate Electron Localization Function (ELF) 3D cube file."""
    runner = MultiwfnRunner(multiwfn_path)
    # Menu 5 -> 9 (ELF) -> grid quality
    commands = [
        "5",   # Output and calculate grid data
        "9",   # Electron Localization Function (ELF)
        str(grid_quality),
        "2",   # Export to cube file
    ]
    return runner.run_commands(input_file=fchk_file, commands=commands)
