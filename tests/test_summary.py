"""Tests for src/summary.py. Run from the project root: python -m pytest"""

import json
from pathlib import Path

import numpy as np

from src.summary import build_summary, write_summary


def make_summary() -> dict:
    return build_summary(
        optimizer="min_distance",
        optimizer_params={"alpha_limit": 0.8, "max_iterations": 200},
        n_left=156,
        n_right=156,
        center_length_m=3912.85,
        line_length_m=3713.93,
        alpha=np.array([-0.8, 0.1, 0.8], dtype=np.float32),  # float32 on purpose
        stage_times_ms={"centerline": 0.5912, "optimizer": 641.2346},
    )


def test_summary_values() -> None:
    summary = make_summary()
    assert summary["optimizer"] == "min_distance"
    assert summary["points"] == {"left": 156, "right": 156}
    assert summary["lengths_m"]["saving"] == 198.92
    assert summary["alpha_range"]["min"] < 0.0 < summary["alpha_range"]["max"]
    assert summary["stage_times_ms"]["optimizer"] == 641.235  # rounded to 3 decimals
    assert "assumed" in summary["notes"]  # units are not claimed as fact


def test_summary_can_be_written_and_read_back(tmp_path: Path) -> None:
    """A float32 alpha must still be writable: this is why float() is used."""
    out_file = tmp_path / "nested" / "run_summary.json"
    summary = make_summary()

    write_summary(summary, out_file)

    assert json.loads(out_file.read_text(encoding="utf-8")) == summary
    assert out_file.read_text(encoding="utf-8").endswith("\n")
