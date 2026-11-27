from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from my_sci_toolkit.simulation.cp2k import (
    CP2KInputBuilder,
    validate_cp2k_input,
    validate_cp2k_output,
    estimate_hirshfeld_charges,
    validate_bader_true_results,
    read_cube,
    validate_cube_compatibility,
    subtract_cube_fields,
    detect_vacuum_plateau,
    validate_vacuum_energy_reference,
    ase_harmonic_thermochemistry,
)
from my_sci_toolkit.viz import apply_figure_profile, add_panel_label, save_figure_profiled


def test_finite_builder_adds_explicit_cluster_controls_and_kind_specific_basis():
    builder = CP2KInputBuilder(project_name="synthetic_cluster", run_type="ENERGY")
    atoms = [("Cu_a", 0.0, 0.0, 0.0), ("Cu_b", 1.0, 0.0, 0.0)]
    kinds = {
        "Cu_a": {"element":"Cu","basis_set":"BASIS-A","potential":"POT-A","valence_electrons":11},
        "Cu_b": {"element":"Cu","basis_set":"BASIS-B","potential":"POT-B","valence_electrons":11},
    }
    text = builder.build_finite_system(
        atoms, {"a":12,"b":12,"c":12}, kind_definitions=kinds,
        cell_periodicity="NONE", poisson_periodicity="NONE", poisson_solver="MT",
        total_charge=0, multiplicity=1, center_coordinates=True,
        xc_functional="PBE", dispersion_model="DFTD3(BJ)",
        dispersion_reference_functional="PBE", cutoff_ry=450,
        scf_method="DIAGONALIZATION", smearing={"temperature_k":300},
        added_mos=6, mixing={"alpha":0.3}, print_sections=["E_DENSITY_CUBE","PDOS"],
    )
    assert "PERIODIC NONE" in text and "PSOLVER MT" in text
    assert "&KIND Cu_a" in text and "BASIS-A" in text
    assert "&KIND Cu_b" in text and "BASIS-B" in text
    assert "&DIAGONALIZATION T" in text
    assert "&SMEAR ON" in text and "&MIXING ON" in text
    assert "ELECTRONIC_TEMPERATURE [K] 300" in text
    assert "ADDED_MOS 6" in text and "&PDOS" in text
    assert text.index("    &END XC") < text.index("    &PRINT") < text.index("    &END PRINT") < text.index("  &END DFT")
    assert text.count("      Cu_") == 2


def test_triclinic_finite_cell_centers_coordinates_at_parallelepiped_center():
    builder = CP2KInputBuilder(project_name="triclinic_cluster", run_type="ENERGY")
    text = builder.build_finite_system(
        [("H", 0.0, 0.0, 0.0)],
        {"a":10,"b":10,"c":10,"alpha":90,"beta":90,"gamma":60},
        kind_definitions={"H":{"element":"H","basis_set":"B","potential":"P","valence_electrons":1}},
        total_charge=0, multiplicity=2, uks=True, center_coordinates=True,
    )
    coordinate_line = next(line for line in text.splitlines() if line.strip().startswith("H "))
    values = [float(value) for value in coordinate_line.split()[1:4]]
    assert values == pytest.approx([7.5, 4.3301270189, 5.0], abs=1e-8)


def test_finite_builder_rejects_missing_kind_bad_parity_and_ot_mixing():
    builder = CP2KInputBuilder(project_name="invalid_cluster", run_type="ENERGY")
    with pytest.raises(ValueError, match="KIND definitions"):
        builder.build_finite_system([("X",0,0,0)],{"a":10,"b":10,"c":10},kind_definitions={})
    kinds={"H":{"element":"H","basis_set":"B","potential":"P","valence_electrons":1}}
    with pytest.raises(ValueError, match="parity"):
        builder.build_finite_system([("H",0,0,0)],{"a":10,"b":10,"c":10},
                                    kind_definitions=kinds,total_charge=0,multiplicity=1)
    cu={"Cu":{"element":"Cu","basis_set":"B","potential":"P","valence_electrons":11}}
    with pytest.raises(ValueError, match="require DIAGONALIZATION"):
        builder.build_finite_system([("Cu",0,0,0)],{"a":10,"b":10,"c":10},
                                    kind_definitions=cu,mixing={"alpha":0.3})


def test_task_aware_output_validation_requires_normal_termination_and_task_evidence(tmp_path):
    log=tmp_path/"calc.out"
    header="CP2K version 2025.2\nSCF run converged\nENERGY| Total FORCE_EVAL ( QS ) energy (a.u.): -1.0\n"
    log.write_text(header,encoding="utf-8")
    assert validate_cp2k_output(log,"ENERGY")["status"]=="failed_or_incomplete"
    log.write_text(header+"PROGRAM ENDED AT now\n",encoding="utf-8")
    assert validate_cp2k_output(log,"ENERGY")["status"]=="passed"
    assert validate_cp2k_output(log,"GEO_OPT")["geometry_optimization_completed"] is False


def test_true_bader_validation_and_approximate_hirshfeld_estimate_are_distinct():
    bader=pd.DataFrame({"atom_id":[1,2],"element":["H","O"],"bader_population":[1.0,6.0]})
    result=validate_bader_true_results(bader,expected_atoms=[(1,"H"),(2,"O")],expected_electron_count=7.0)
    assert result["passed"] and result["method"]=="true_bader_density_basin"
    with pytest.raises(ValueError,match="atom order"):
        validate_bader_true_results(bader.iloc[::-1],expected_atoms=[(1,"H"),(2,"O")])
    hirshfeld=pd.DataFrame({"atom_id":[1,2],"element":["H","O"],"net_charge":[0.2,-0.1]})
    estimated=estimate_hirshfeld_charges(
        hirshfeld,valence_electrons={"H":1,"O":6},scaling_factors={"H":1.5,"O":2.0}
    )
    assert estimated["charge_method"].iloc[0]=="approximate_calibrated_hirshfeld_estimate"
    assert estimated["charge_residual"].iloc[0]==pytest.approx(0.1)
    assert "bader_population" not in estimated.columns


def test_cube_subtraction_requires_identical_grid_and_atom_mapping(tmp_path):
    def write_cube(path, atomic_number=1, origin="0 0 0", x_count=2):
        values="0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8"
        path.write_text("\n".join([
            "cube synthetic", "density fixture", f"1 {origin}",
            f"{x_count} 1 0 0", "2 0 1 0", "2 0 0 1",
            f"{atomic_number} {atomic_number}.0 0.0 0.0 0.0", values,
        ])+"\n",encoding="utf-8")
    first=tmp_path/"first.cube"; second=tmp_path/"second.cube"
    write_cube(first); write_cube(second)
    a,b=read_cube(first),read_cube(second)
    assert validate_cube_compatibility(a,b)["compatible"]
    assert np.allclose(subtract_cube_fields(a,b),0)
    write_cube(second,atomic_number=8)
    with pytest.raises(ValueError,match="incompatible"):
        subtract_cube_fields(a,read_cube(second))


def test_cube_coordinate_unit_sign_is_preserved_and_mixed_units_are_rejected(tmp_path):
    def write_cube(path, signed_count):
        path.write_text("\n".join([
            "cube", "unit fixture", "1 0 0 0",
            f"{signed_count} 1 0 0", f"{signed_count} 0 1 0", f"{signed_count} 0 0 1",
            "1 1.0 0.0 0.0 0.0", "0.1 0.2 0.3 0.4",
        ])+"\n",encoding="utf-8")
    ang=tmp_path/"angstrom.cube"; bohr=tmp_path/"bohr.cube"
    write_cube(ang,2); write_cube(bohr,-2)
    a,b=read_cube(ang),read_cube(bohr)
    assert a["coordinate_unit"]=="angstrom"
    assert b["coordinate_unit"]=="bohr"
    with pytest.raises(ValueError,match="coordinate_unit_mismatch"):
        subtract_cube_fields(a,b)
    mixed=tmp_path/"mixed.cube"
    mixed.write_text("\n".join([
        "cube","mixed fixture","1 0 0 0","2 1 0 0","-2 0 1 0","2 0 0 1",
        "1 1.0 0.0 0.0 0.0","0.1 0.2 0.3 0.4",
    ])+"\n",encoding="utf-8")
    with pytest.raises(ValueError,match="mixed coordinate-unit signs"):
        read_cube(mixed)


def test_vacuum_plateau_and_energy_reference_are_fail_closed():
    plateau=detect_vacuum_plateau(
        [0,1,2,3,4],[1.0,2.0,2.001,2.0,2.001],
        z_min=1,z_max=4,max_spread=0.01,max_abs_slope=0.01,
    )
    assert plateau["passed"]
    accepted=validate_vacuum_energy_reference(
        potential_quantity="electrostatic_potential",
        reference_zero="documented_cp2k_electrostatic_potential_zero",
        plateau_report=plateau,reference_energy_eV=3.2,
    )
    assert accepted["supported"]
    rejected=validate_vacuum_energy_reference(
        potential_quantity="density",
        reference_zero="unknown",plateau_report=plateau,reference_energy_eV=3.2,
    )
    assert not rejected["supported"]


def test_explicit_figure_profile_can_export_and_reject_unknown_keys(tmp_path):
    profile={"background":"white","width_in":3.3,"height_in":2.4,"font_family":"Arial",
             "font_size":7,"palette":"nature","dpi":300,"panel_label_size":8}
    assert apply_figure_profile(profile)["dpi"]==300
    fig,ax=plt.subplots()
    add_panel_label(ax,"a",profile)
    target=save_figure_profiled(fig,tmp_path/"synthetic.png",profile,metadata={"Creator":"synthetic-test"})
    assert target.exists()
    assert fig.get_size_inches()[0]==pytest.approx(3.3)
    plt.close(fig)
    with pytest.raises(ValueError,match="unknown figure profile"):
        apply_figure_profile({"project_default":True})


def test_ase_wrapper_requires_explicit_mode_scope_and_optional_runtime():
    with pytest.raises(ValueError,match="selected_atom_indices"):
        ase_harmonic_thermochemistry([100,200],temperature_K=298.15,mode_scope="adsorbate_subspace")
    try:
        result=ase_harmonic_thermochemistry([100,200,300],temperature_K=298.15,mode_scope="full_system")
    except ImportError:
        pytest.skip("ASE optional dependency is not installed in the CI core environment")
    assert result["thermochemistry_engine"]=="ASE HarmonicThermo"
    assert result["temperature_K"]==298.15
    assert result["ideal_gas_treatment"] is False


def test_cp2k_input_linter_wrapper_reports_optional_dependency(monkeypatch,tmp_path):
    source=tmp_path/"input.inp"
    source.write_text("&GLOBAL\n&END GLOBAL\n",encoding="utf-8")
    monkeypatch.setattr("my_sci_toolkit.simulation.cp2k.dft_workflows.shutil.which",lambda name: None)
    with pytest.raises(FileNotFoundError,match="cp2klint"):
        validate_cp2k_input(source)
