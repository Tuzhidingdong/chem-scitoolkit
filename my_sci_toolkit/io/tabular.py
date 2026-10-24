"""Tabular data ingestion routines for spectra, kinetic traces, and logs."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Union
from my_sci_toolkit.core.paths import list_files, extract_time_from_stem


def read_xy(file_path: str | Path, delimiter: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Read a two-column (X, Y) text/xy file.

    Args:
        file_path: Path to the data file.
        delimiter: Specific separator or whitespace if None.

    Returns:
        Tuple[np.ndarray, np.ndarray]: (x_array, y_array).
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    # Use pandas for fast C-level parsing with comment and whitespace handling
    df = pd.read_csv(p, sep=delimiter or r"\s+", header=None, comment="#", engine="python")
    # Take first two numeric columns
    x = df.iloc[:, 0].to_numpy(dtype=float)
    y = df.iloc[:, 1].to_numpy(dtype=float)
    return x, y


def read_xy_series_dir(
    directory: str | Path,
    patterns: Optional[List[str]] = None,
    time_slice: Optional[Tuple[int, int]] = None,
) -> Tuple[np.ndarray, List[np.ndarray], List[float]]:
    """Read an ordered series of spectra from a directory.

    Args:
        directory: Folder containing sequential measurement files.
        patterns: Glob pattern list (e.g. ['*.xy']).
        time_slice: Slice indices on filename stem to extract timestamps.

    Returns:
        Tuple:
            - x_axis: Shared 1D x axis.
            - y_series: List of 1D intensity arrays.
            - timestamps: Extracted timestamps corresponding to files.
    """
    files = list_files(directory, patterns or ["*.xy", "*.txt", "*.csv"])
    if not files:
        raise ValueError(f"No matching files found in directory: {directory}")

    timestamps = []
    y_series = []
    x_axis = None

    for f in files:
        x, y = read_xy(f)
        if x_axis is None:
            x_axis = x
        y_series.append(y)
        t = extract_time_from_stem(f.stem, time_slice)
        timestamps.append(t)

    return x_axis, y_series, timestamps


def read_excel_columns(
    file_path: str | Path,
    x_col: str | int = 0,
    y_cols: Union[str | int, List[Union[str | int]]] = 1,
    sheet_name: Union[str, int] = 0,
) -> Tuple[np.ndarray, Union[np.ndarray, List[np.ndarray]]]:
    """Read specific columns from an Excel spreadsheet."""
    p = Path(file_path)
    df = pd.read_excel(p, sheet_name=sheet_name)
    
    x = df.iloc[:, x_col].to_numpy(dtype=float) if isinstance(x_col, int) else df[x_col].to_numpy(dtype=float)
    
    if isinstance(y_cols, (str, int)):
        y = df.iloc[:, y_cols].to_numpy(dtype=float) if isinstance(y_cols, int) else df[y_cols].to_numpy(dtype=float)
        return x, y

    y_list = []
    for col in y_cols:
        val = df.iloc[:, col].to_numpy(dtype=float) if isinstance(col, int) else df[col].to_numpy(dtype=float)
        y_list.append(val)
    return x, y_list
