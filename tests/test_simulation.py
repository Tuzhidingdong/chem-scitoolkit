"""Tests for multi-code simulation builders (CP2K, VASP, ORCA, LAMMPS, SLURM)."""

import pytest
from pathlib import Path
from my_sci_toolkit.simulation.cp2k import CP2KInputBuilder
from my_sci_toolkit.simulation.vasp import VASPInputBuilder
from my_sci_toolkit.simulation.orca import ORCAInputBuilder
from my_sci_toolkit.simulation.slurm import generate_slurm_script


def test_cp2k_builder_from_structure():
    builder = CP2KInputBuilder(project_name="water_test", run_type="GEO_OPT", functional="PBE")
    cell = {"a": 12.0, "b": 12.0, "c": 12.0, "alpha": 90.0, "beta": 90.0, "gamma": 90.0}
    atoms = [("O", 0.0, 0.0, 0.0), ("H", 0.75, 0.58, 0.0), ("H", -0.75, 0.58, 0.0)]

    inp_text = builder.build_from_structure(cell, atoms)
    assert "&GLOBAL" in inp_text
    assert "PROJECT water_test" in inp_text
    assert "&FORCE_EVAL" in inp_text
    assert "ABC 12.0000 12.0000 12.0000" in inp_text
    assert "O " in inp_text and "0.000000" in inp_text
    assert "&KIND O" in inp_text
    assert "&KIND H" in inp_text


def test_vasp_builder():
    builder = VASPInputBuilder(incar_params={"ENCUT": 520, "ISIF": 3}, kpoints_mesh=(4, 4, 1))
    incar_str = builder.build_incar()
    kpoints_str = builder.build_kpoints()

    assert "ENCUT        = 520" in incar_str
    assert "ISIF         = 3" in incar_str
    assert "4 4 1" in kpoints_str


def test_orca_builder():
    builder = ORCAInputBuilder(method="B3LYP", basis="def2-TZVP", task="Opt")
    atoms = [("C", 0.0, 0.0, 0.0), ("O", 0.0, 0.0, 1.15)]
    orca_str = builder.build_from_coordinates(atoms)

    assert "! B3LYP def2-TZVP Opt" in orca_str
    assert "* xyz 0 1" in orca_str
    assert "C" in orca_str and "O" in orca_str


def test_slurm_script_generator():
    slurm_cp2k = generate_slurm_script(job_name="cp2k_calc", software="cp2k", nodes=2, ntasks_per_node=32)
    assert "#SBATCH -J cp2k_calc" in slurm_cp2k
    assert "#SBATCH -N 2" in slurm_cp2k
    assert "mpirun -np 64 cp2k.popt" in slurm_cp2k

    slurm_vasp = generate_slurm_script(job_name="vasp_calc", software="vasp", nodes=1, ntasks_per_node=64)
    assert "mpirun -np 64 vasp_std" in slurm_vasp
