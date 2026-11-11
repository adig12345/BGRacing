"""Tests for src/optimizers.py. Run from the project root: python -m pytest"""
from pathlib import Path

import numpy as np
import pytest

from src.geometry import Corridor, apply_offsets, build_corridor, load_track, path_length
from src.optimizers import OPTIMIZERS, get_optimizer, register

REAL_CSV = Path(__file__).parent.parent / "data" / "BrandsHatchLayout.csv"
PARAMS = {"alpha_limit": 0.9, "max_iterations": 200, "tolerance": 1e-9}


def make_ring_corridor(n: int = 36, radius: float = 10.0, half_width: float = 2.0) -> Corridor:
    """A circular road: center on a circle, lateral vectors pointing outward."""
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    outward = np.stack([np.cos(angles), np.sin(angles)], axis=1)  # unit vectors
    return Corridor(center=radius * outward, lateral=half_width * outward)


def test_builtin_optimizers_are_registered() -> None:
    assert {"centerline", "min_distance"} <= set(OPTIMIZERS)


def test_unknown_optimizer_error_lists_available_names() -> None:
    with pytest.raises(ValueError, match="Available"):
        get_optimizer("does_not_exist")


def test_duplicate_registration_is_rejected() -> None:
    with pytest.raises(ValueError, match="already registered"):
        register("centerline")(lambda corridor, params: np.zeros(1))


def test_centerline_optimizer_returns_zeros() -> None:
    corridor = make_ring_corridor()
    alpha = get_optimizer("centerline")(corridor, {})
    np.testing.assert_array_equal(alpha, np.zeros(36))


def test_min_distance_on_a_ring_hugs_the_inner_edge() -> None:
    """On a circular road the shortest line is the inner circle.

    The lateral vectors point outward, so the inner edge is alpha = -limit.
    The line then has radius 10 - 2 * 0.9 = 8.2 at every point.
    """
    corridor = make_ring_corridor()
    alpha = get_optimizer("min_distance")(corridor, PARAMS)
    np.testing.assert_allclose(alpha, -PARAMS["alpha_limit"], atol=1e-6)
    radii = np.linalg.norm(apply_offsets(corridor, alpha), axis=1)
    np.testing.assert_allclose(radii, 8.2, atol=1e-6)


def test_min_distance_on_real_track() -> None:
    """Stays inside the limit and is clearly shorter than the centerline."""
    corridor = build_corridor(load_track(REAL_CSV))
    alpha = get_optimizer("min_distance")(corridor, PARAMS)
    assert np.abs(alpha).max() <= PARAMS["alpha_limit"] + 1e-12
    center_length = path_length(corridor.center)
    line_length = path_length(apply_offsets(corridor, alpha))
    assert line_length < center_length
    assert line_length == pytest.approx(3689.9, abs=0.1)
