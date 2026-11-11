"""Tests for src/plotting.py. Run from the project root: python -m pytest"""

from pathlib import Path

import numpy as np

from src.geometry import Track, build_corridor
from src.plotting import _closed, save_result_plot


def test_closed_repeats_first_point_and_keeps_input() -> None:
    points = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    closed = _closed(points)
    assert closed.shape == (4, 2)
    np.testing.assert_array_equal(closed[-1], closed[0])
    assert points.shape == (3, 2)  # the input array was not modified


def test_save_result_plot_creates_a_png_and_the_folder(
    tmp_path: Path, outer_square, inner_square
) -> None:
    track = Track(left=outer_square, right=inner_square)
    corridor = build_corridor(track)
    out_file = tmp_path / "new_folder" / "plot.png"  # folder does not exist yet

    save_result_plot(track, corridor, corridor.center, out_file, title="test")

    assert out_file.exists()
    assert out_file.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"  # PNG file signature
