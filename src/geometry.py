"""Pure geometry helpers for the track. No ROS imports allowed in this file."""
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Track:
    """Left and right track boundaries.
    Each is an (N, 2) float array: one row per point, columns are [x, y].
    """
    left: np.ndarray
    right: np.ndarray


def load_track(csv_path: Path) -> Track:
    """Read the CSV (columns: x, y, side) and return clean boundaries.
    Rows with empty x or y become NaN while reading and are then removed.
    """
    sides = {'left': [], 'right': []} 

    with open(csv_path) as f:
        for row in csv.DictReader(f):
            side = (row.get('side') or '').strip().lower()
            try:
                x = float(row['x']) if row['x'] else float('nan')
                y = float(row['y']) if row['y'] else float('nan')
            except (TypeError, ValueError):
                continue # TODO: logs

            if side in sides:
                sides[side].append([x,y])

    def clean_boundary(points):
        a = np.array(points, dtype=float).reshape(-1, 2)
        return a[np.isfinite(a).all(axis=1)]

    left = clean_boundary(sides['left'])
    right = clean_boundary(sides['right'])

    return Track(left=left, right=right)
