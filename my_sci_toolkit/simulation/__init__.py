"""Computational chemistry and molecular simulation package.

Subpackages:
- cp2k: CP2K input builder (from CIF/coords), metadynamics colvars, and log parser.
- vasp: VASP INCAR, KPOINTS, POSCAR generation and OUTCAR/OSZICAR extraction.
- orca: Molecular DFT and wavefunction input builder and frequency parser.
- multiwfn: Automated Multiwfn batch runner, Bader charge, ESP, and COHP/LDOS pipelines.
- lammps: Classical MD data file builder and force field control scripts.
- ml_potentials: MACE / DeepMD training script generators and ASE dynamics runner.
- slurm: HPC cluster submission script generators.
"""

from my_sci_toolkit.simulation.base import (
    BaseInputBuilder,
    BaseParser,
    BaseRunner,
    CalculationConfig,
)
from my_sci_toolkit.simulation.cp2k import (
    CP2KInputBuilder,
    build_cp2k_from_cif,
    CP2KParser,
)
from my_sci_toolkit.simulation.vasp import (
    VASPInputBuilder,
    write_vasp_inputs,
    VASPParser,
)
from my_sci_toolkit.simulation.orca import (
    ORCAInputBuilder,
    write_orca_input,
    ORCAParser,
)
from my_sci_toolkit.simulation.multiwfn import (
    MultiwfnRunner,
    run_bader_charge_analysis,
    run_esp_surface_analysis,
    calculate_cohp_fragments,
)
from my_sci_toolkit.simulation.lammps import (
    write_lammps_data,
    LAMMPSInputBuilder,
)
from my_sci_toolkit.simulation.ml_potentials import (
    generate_mace_training_command,
    generate_deepmd_input,
    MLPDynamicsRunner,
)
from my_sci_toolkit.simulation.slurm import (
    generate_slurm_script,
)

__all__ = [
    "BaseInputBuilder",
    "BaseParser",
    "BaseRunner",
    "CalculationConfig",
    "CP2KInputBuilder",
    "build_cp2k_from_cif",
    "CP2KParser",
    "VASPInputBuilder",
    "write_vasp_inputs",
    "VASPParser",
    "ORCAInputBuilder",
    "write_orca_input",
    "ORCAParser",
    "MultiwfnRunner",
    "run_bader_charge_analysis",
    "run_esp_surface_analysis",
    "calculate_cohp_fragments",
    "write_lammps_data",
    "LAMMPSInputBuilder",
    "generate_mace_training_command",
    "generate_deepmd_input",
    "MLPDynamicsRunner",
    "generate_slurm_script",
]
