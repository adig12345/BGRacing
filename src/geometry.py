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


@dataclass(frozen=True)
class Corridor:
    """The drivable corridor: its middle line and its sideways half-vectors.

    center[i]  : centerline point c_i, shape (N, 2).
    lateral[i] : vector d_i from c_i to the left boundary, shape (N, 2).

    A line is described by one offset alpha_i per point:
        point_i = center[i] + alpha_i * lateral[i]
    alpha = 0 is the centerline, +1 the left boundary, -1 the right boundary.
    """

    center: np.ndarray
    lateral: np.ndarray


def build_corridor(track: Track) -> Corridor:
    """Build the corridor from a track (left[i] must pair with right[i])."""
    center = compute_centerline(track)
    # center = (left + right) / 2, so left - center = (left - right) / 2.
    lateral = (track.left - track.right) / 2
    return Corridor(center=center, lateral=lateral)


def apply_offsets(corridor: Corridor, alpha: np.ndarray) -> np.ndarray:
    """Return the (N, 2) points of the line described by the offsets `alpha`."""
    if alpha.shape != (len(corridor.center),):
        raise ValueError(
            f"alpha must have shape ({len(corridor.center)},), got {alpha.shape}"
        )
    return corridor.center + alpha[:, np.newaxis] * corridor.lateral
