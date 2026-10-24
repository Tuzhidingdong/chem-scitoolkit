"""HPC Cluster SLURM submission script generator (*.sh, *.slurm)."""

from pathlib import Path
from typing import Optional


def generate_slurm_script(
    job_name: str = "chem_job",
    software: str = "cp2k",  # cp2k, vasp, orca, lammps
    nodes: int = 1,
    ntasks_per_node: int = 64,
    partition: str = "compute",
    time_limit: str = "48:00:00",
    cp2k_inp: str = "cp2k.inp",
    output_sh: Optional[str | Path] = None,
) -> str:
    """Generate high-performance computing SLURM batch execution script.

    Refactored from cp2kMD.shgenerate and vaspsh.
    """
    total_cores = nodes * ntasks_per_node
    lines = [
        "#!/bin/bash",
        f"#SBATCH -J {job_name}",
        f"#SBATCH -p {partition}",
        f"#SBATCH -N {nodes}",
        f"#SBATCH --ntasks-per-node={ntasks_per_node}",
        f"#SBATCH -t {time_limit}",
        f"#SBATCH -o %j.out",
        f"#SBATCH -e %j.err",
        "",
        "# Module loading and environment setup",
        "ulimit -s unlimited",
        "export OMP_NUM_THREADS=1",
        "",
    ]

    soft_lower = software.lower()
    if soft_lower == "cp2k":
        lines.extend([
            "# module load cp2k/8.1",
            f"mpirun -np {total_cores} cp2k.popt -i {cp2k_inp} -o cp2k.out",
        ])
    elif soft_lower == "vasp":
        lines.extend([
            "# module load vasp/6.3.0",
            f"mpirun -np {total_cores} vasp_std > vasp.out",
        ])
    elif soft_lower == "orca":
        lines.extend([
            "# module load orca/5.0.3",
            f"$(which orca) orca.inp > orca.out",
        ])
    elif soft_lower == "lammps":
        lines.extend([
            "# module load lammps/2023",
            f"mpirun -np {total_cores} lmp_mpi -in in.lammps > lmp.out",
        ])

    script_text = "\n".join(lines) + "\n"

    if output_sh:
        out_p = Path(output_sh)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(script_text)

    return script_text
