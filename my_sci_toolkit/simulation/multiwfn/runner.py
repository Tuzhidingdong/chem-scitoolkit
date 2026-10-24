"""Multiwfn binary locator, command runner, and silent batch pipeline."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from my_sci_toolkit.simulation.base import BaseRunner


class MultiwfnRunner(BaseRunner):
    """External Multiwfn executable runner with automated path discovery."""

    def _find_executable(self, custom_path: Optional[str | Path] = None) -> Optional[Path]:
        """Discover Multiwfn.exe across environment PATH and standard research paths."""
        if custom_path:
            p = Path(custom_path)
            if p.exists():
                return p.resolve()

        # Check system PATH
        which_path = shutil.which("Multiwfn") or shutil.which("Multiwfn.exe")
        if which_path:
            return Path(which_path)

        # Common Windows paths from user's current machine
        common_locations = [
            Path(r"D:\Software\Multiwfn_2026.7.15_bin_Win64\Multiwfn.exe"),
            Path(r"C:\Multiwfn\Multiwfn.exe"),
            Path(r"D:\Multiwfn\Multiwfn.exe"),
        ]
        for loc in common_locations:
            if loc.exists():
                return loc.resolve()

        return None

    def run_commands(
        self,
        input_file: str | Path,
        commands: List[str],
        output_dir: Optional[str | Path] = None,
        timeout_sec: int = 300,
    ) -> Dict[str, Any]:
        """Execute Multiwfn silently with a sequential stream of menu commands."""
        in_p = Path(input_file).resolve()
        if not in_p.exists():
            raise FileNotFoundError(f"Wavefunction/coordinate file not found: {in_p}")

        if not self.executable_path:
            return {
                "status": "error",
                "message": "Multiwfn executable not found in PATH or standard installation directories.",
            }

        out_d = Path(output_dir) if output_dir else in_p.parent
        out_d.mkdir(parents=True, exist_ok=True)

        cmd_stream = "\n".join(commands) + "\nq\n"
        process = subprocess.Popen(
            [str(self.executable_path), str(in_p), "-isilent"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(out_d),
            text=True,
        )

        try:
            stdout, stderr = process.communicate(input=cmd_stream, timeout=timeout_sec)
            return {
                "status": "success",
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "cwd": str(out_d),
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "status": "timeout",
                "message": f"Multiwfn execution timed out after {timeout_sec} seconds.",
            }

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        return self.run_commands(*args, **kwargs)
