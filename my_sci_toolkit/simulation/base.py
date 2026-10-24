"""Base abstract classes and protocol definitions for computational chemistry builders and runners."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field


@dataclass
class CalculationConfig:
    """General calculation parameter container."""
    project_name: str = "calc"
    charge: int = 0
    multiplicity: int = 1
    functional: str = "PBE"
    basis_set: str = "DZVP-MOLOPT-SR-GTH"
    dispersion: Optional[str] = "D3"
    run_type: str = "ENERGY_FORCE"  # e.g., GEO_OPT, MD, CELL_OPT
    periodic: str = "XYZ"  # XYZ, NONE, X, Y, Z
    extra_params: Dict[str, Any] = field(default_factory=dict)


class BaseInputBuilder(ABC):
    """Abstract base class for all computational input file builders (CP2K, VASP, ORCA, LAMMPS)."""

    def __init__(self, config: Optional[CalculationConfig] = None):
        self.config = config or CalculationConfig()

    @abstractmethod
    def build(self, **kwargs) -> str:
        """Construct the input file contents as a string."""
        pass

    def write(self, output_path: str | Path, **kwargs) -> Path:
        """Write the constructed input configuration to a file on disk."""
        content = self.build(**kwargs)
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(content)
        return out_p.resolve()


class BaseParser(ABC):
    """Abstract base class for parsing quantum chemistry and molecular dynamics outputs."""

    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        if not self.log_path.exists():
            raise FileNotFoundError(f"Output file does not exist: {self.log_path}")

    @abstractmethod
    def get_final_energy(self) -> Optional[float]:
        """Extract final total energy in eV or Hartree."""
        pass

    @abstractmethod
    def is_converged(self) -> bool:
        """Determine whether the geometry optimization or SCF cycle converged."""
        pass


class BaseRunner(ABC):
    """Abstract runner for invoking external binaries (Multiwfn, CP2K, etc.)."""

    def __init__(self, executable_path: Optional[str | Path] = None):
        self.executable_path = self._find_executable(executable_path)

    @abstractmethod
    def _find_executable(self, custom_path: Optional[str | Path] = None) -> Optional[Path]:
        """Locate external program binary."""
        pass

    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute command and return structured results."""
        pass
