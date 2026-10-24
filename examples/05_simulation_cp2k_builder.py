"""Example 5: Simulation builders (CP2K, VASP, and SLURM Cluster Scripts).

Demonstrates modular quantum chemistry engineering refactored from cp2kMD.py.
"""

from pathlib import Path
from my_sci_toolkit.simulation.cp2k import CP2KInputBuilder
from my_sci_toolkit.simulation.vasp import write_vasp_inputs
from my_sci_toolkit.simulation.slurm import generate_slurm_script

output_dir = Path("./outputs")
output_dir.mkdir(exist_ok=True)

# 1. Build CP2K input from cell and atoms
builder = CP2KInputBuilder(
    project_name="FeS_water_interface",
    run_type="GEO_OPT",
    functional="PBE",
    cutoff_ry=450,
)
cell = {"a": 10.5, "b": 10.5, "c": 25.0, "alpha": 90.0, "beta": 90.0, "gamma": 90.0}
atoms = [
    ("Fe", 0.0, 0.0, 5.0),
    ("S", 1.8, 1.8, 5.0),
    ("O", 0.0, 0.0, 8.5),
    ("H", 0.7, 0.5, 8.5),
    ("H", -0.7, 0.5, 8.5),
]
cp2k_inp = builder.build_from_structure(cell, atoms)
inp_path = output_dir / "cp2k_example.inp"
with open(inp_path, "w", encoding="utf-8") as f:
    f.write(cp2k_inp)
print(f"Generated CP2K input file: {inp_path}")

# 2. Build VASP INCAR & KPOINTS
vasp_files = write_vasp_inputs(
    output_dir=output_dir / "vasp_calc",
    incar_params={"ENCUT": 500, "ISIF": 2, "EDIFFG": -0.01},
    kpoints_mesh=(3, 3, 1),
)
print(f"Generated VASP inputs: {vasp_files}")

# 3. Generate SLURM supercomputer submission script
slurm_path = output_dir / "run_cp2k.sh"
generate_slurm_script(
    job_name="FeS_OPT",
    software="cp2k",
    nodes=2,
    ntasks_per_node=64,
    cp2k_inp=str(inp_path.name),
    output_sh=slurm_path,
)
print(f"Generated SLURM script: {slurm_path}")
