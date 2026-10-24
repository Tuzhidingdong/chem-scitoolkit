"""Safe filesystem path utilities to eliminate os.chdir and hardcoded paths."""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple


def resolve_path(target: str | Path, base_dir: Optional[str | Path] = None) -> Path:
    """Resolve a path safely without altering process working directory."""
    p = Path(target)
    if p.is_absolute():
        return p
    base = Path(base_dir) if base_dir else Path.cwd()
    return (base / p).resolve()


def list_files(
    directory: str | Path,
    patterns: Optional[List[str]] = None,
    sort: bool = True,
) -> List[Path]:
    """List all files in directory matching specified extensions/patterns.

    Args:
        directory: Directory path.
        patterns: List of glob patterns (e.g. ['*.xy', '*.csv', '*.txt']).
        sort: Whether to sort files naturally.

    Returns:
        List[Path]: Collected file paths.
    """
    d = Path(directory)
    if not d.exists() or not d.is_dir():
        return []

    if not patterns:
        patterns = ["*.*"]

    found: List[Path] = []
    for pat in patterns:
        found.extend(d.glob(pat))

    if sort:
        def natural_sort_key(p: Path):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', p.name)]
        found.sort(key=natural_sort_key)

    return found


def extract_time_from_stem(stem: str, slice_range: Optional[Tuple[int, int]] = None) -> float:
    """Extract numeric time label from a filename stem.

    Examples:
        '010_xrd.xy' -> 10.0
        'time_240.txt' -> 240.0
    """
    if slice_range:
        candidate = stem[slice_range[0]:slice_range[1]]
        try:
            return float(candidate)
        except ValueError:
            pass

    digits = re.findall(r"[-+]?\d*\.\d+|\d+", stem)
    if digits:
        return float(digits[0])
    return 0.0
