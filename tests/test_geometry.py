"""Tests for src/geometry.py. Run from the project root: python -m pytest"""

from pathlib import Path

import numpy as np
import pytest

from src.geometry import Track, compute_centerline, load_track, path_length

REAL_CSV = Path(__file__).parent.parent / "data" / "BrandsHatchLayout.csv"


def test_centerline_of_concentric_squares(outer_square, inner_square) -> None:
    """Midpoints of the outer and inner squares are the square at +-2."""
    track = Track(left=outer_square, right=inner_square)
    expected = np.array([[-2, -2], [2, -2], [2, 2], [-2, 2]], dtype=float)
    np.testing.assert_allclose(compute_centerline(track), expected)


def test_centerline_rejects_unequal_lengths(outer_square, inner_square) -> None:
    """Pairing by index is meaningless if the sides differ in length."""
    track = Track(left=outer_square, right=inner_square[:3])  # 4 points vs 3 points
    with pytest.raises(ValueError):
        compute_centerline(track)


def test_path_length_closed_and_open() -> None:
    """The square at +-2 has sides of 4: closed = 16, open skips one side."""
    square = np.array([[-2, -2], [2, -2], [2, 2], [-2, 2]], dtype=float)
    assert path_length(square, closed=True) == pytest.approx(16.0)
    assert path_length(square, closed=False) == pytest.approx(12.0)


def test_load_track_drops_blank_rows(tmp_path: Path) -> None:
    """Rows with empty x/y are removed from each side."""
    csv_file = tmp_path / "mini.csv"
    csv_file.write_text(
        "x,y,side\n,,left\n1.0,2.0,left\n3.0,4.0,left\n,,right\n5.0,6.0,right\n"
    )
    track = load_track(csv_file)
    assert track.left.shape == (2, 2)
    assert track.right.shape == (1, 2)
    assert np.isfinite(track.left).all()


def test_load_track_rejects_unknown_side(tmp_path: Path) -> None:
    """A side other than left/right is an error that names the line."""
    csv_file = tmp_path / "bad_side.csv"
    csv_file.write_text("x,y,side\n1.0,2.0,left\n3.0,4.0,middle\n")
    with pytest.raises(ValueError, match="line 3.*unknown side"):
        load_track(csv_file)


def test_load_track_rejects_non_numeric_value(tmp_path: Path) -> None:
    """Text where a number is expected is an error that names the line."""
    csv_file = tmp_path / "bad_number.csv"
    csv_file.write_text("x,y,side\n1.0,abc,left\n")
    with pytest.raises(ValueError, match="line 2.*must be numbers"):
        load_track(csv_file)


def test_real_dataset_numbers() -> None:
    """The real CSV gives 156 points per side and a ~3912.8 m centerline."""
    track = load_track(REAL_CSV)
    assert track.left.shape == (156, 2)
    assert track.right.shape == (156, 2)
    centerline = compute_centerline(track)
    assert path_length(centerline) == pytest.approx(3912.8, abs=0.1)
