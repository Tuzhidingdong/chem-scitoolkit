"""LAMMPS input script generator (in.*) for standard NVT/NPT and water models."""

from pathlib import Path
from typing import Optional, Dict, Any
from my_sci_toolkit.simulation.base import BaseInputBuilder


class LAMMPSInputBuilder(BaseInputBuilder):
    """Builder for LAMMPS molecular dynamics control scripts (*.in)."""

    def __init__(
        self,
        data_file: str = "system.data",
        timestep_fs: float = 1.0,
        temperature_k: float = 300.0,
        pressure_bar: float = 1.0,
        ensemble: str = "nvt",  # nvt, npt, nve
        steps: int = 50000,
        dump_freq: int = 500,
        thermo_freq: int = 100,
    ):
        super().__init__()
        self.data_file = data_file
        self.timestep_fs = timestep_fs
        self.temperature_k = temperature_k
        self.pressure_bar = pressure_bar
        self.ensemble = ensemble.lower()
        self.steps = steps
        self.dump_freq = dump_freq
        self.thermo_freq = thermo_freq

    def build_tip4p_water_script(self) -> str:
        """Construct input script configured for TIP4P/2005 water model."""
        lines = [
            "# LAMMPS input for TIP4P/2005 water simulation",
            "units           real",
            "atom_style      full",
            "boundary        p p p",
            "",
            f"read_data       {self.data_file}",
            "",
            "pair_style      lj/cut/tip4p/long 1 2 1 1 0.1546 8.5 8.5",
            "kspace_style    pppm/tip4p 1.0e-4",
            "",
            "pair_coeff      1 1 0.1852 3.1589  # O-O",
            "pair_coeff      2 2 0.0000 0.0000  # H-H",
            "pair_coeff      1 2 0.0000 0.0000  # O-H",
            "",
            "bond_style      harmonic",
            "bond_coeff      1 0.0 0.9572",
            "angle_style     harmonic",
            "angle_coeff     1 0.0 104.52",
            "",
            f"timestep        {self.timestep_fs}",
            f"thermo          {self.thermo_freq}",
            "thermo_style    custom step temp pe ke etotal press vol",
            "",
            "velocity        all create 300.0 12345 dist gaussian",
            "fix             1 all shake 1e-4 20 0 b 1 a 1",
        ]

        if self.ensemble == "npt":
            lines.append(f"fix             2 all npt temp {self.temperature_k} {self.temperature_k} 100.0 iso {self.pressure_bar} {self.pressure_bar} 1000.0")
        else:
            lines.append(f"fix             2 all nvt temp {self.temperature_k} {self.temperature_k} 100.0")

        lines.extend([
            f"dump            1 all custom {self.dump_freq} traj.lammpstrj id type x y z vx vy vz",
            f"run             {self.steps}",
            "write_data      final.data",
        ])

        return "\n".join(lines)

    def build(self, **kwargs) -> str:
        return self.build_tip4p_water_script()
