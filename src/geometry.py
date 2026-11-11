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


def compute_centerline(track: Track) -> np.ndarray:
    """Return the (N, 2) midpoints between matching left and right points.

    Assumes left[i] and right[i] are a matched pair (true for the Brands Hatch
    CSV). Raises ValueError if the two sides have different lengths, because
    pairing by index would then give a silently wrong centerline.
    """
    if track.left.shape != track.right.shape:
        raise ValueError(
            f"Cannot pair boundaries: left has {len(track.left)} points, "
            f"right has {len(track.right)}"
        )
    return (track.left + track.right) / 2    


def path_length(points: np.ndarray, closed: bool = True) -> float:
    """Total length of the polyline through `points`, in the same units.

    If `closed` is True, the segment from the last point back to the first is
    included (the track is a loop).
    """
    # Vector from each point to the next one; roll(-1) makes row i hold point i+1.
    next_points = np.roll(points, -1, axis=0)
    segments = next_points - points
    lengths = np.linalg.norm(segments, axis=1)
    if not closed:
        lengths = lengths[:-1]  # drop the wrap-around segment (last -> first)
    return float(lengths.sum())
