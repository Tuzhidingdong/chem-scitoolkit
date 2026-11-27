from __future__ import annotations

import pytest

from my_sci_toolkit.simulation.cp2k.dft_workflows import normalize_cp2k_pdos


def test_pdos_wrapper_fails_explicitly_when_optional_cli_is_missing(monkeypatch):
    monkeypatch.setattr("my_sci_toolkit.simulation.cp2k.dft_workflows.shutil.which",lambda name: None)
    with pytest.raises(FileNotFoundError,match="cp2k_pdos"):
        normalize_cp2k_pdos(["synthetic.pdos"])


def test_pdos_wrapper_requires_validated_vacuum_plateau(monkeypatch,tmp_path):
    executable=tmp_path/"cp2k_pdos"
    executable.write_text("",encoding="utf-8")
    executable.chmod(0o755)
    pdos=tmp_path/"input.pdos"
    pdos.write_text("synthetic",encoding="utf-8")
    monkeypatch.setattr("my_sci_toolkit.simulation.cp2k.dft_workflows.shutil.which",lambda name: str(executable))
    with pytest.raises(ValueError,match="validated plateau"):
        normalize_cp2k_pdos([pdos],energy_alignment="vacuum",vacuum_minus_fermi_eV=1.0)
