"""Run summary: a plain dict describing one run, saved as JSON. No ROS imports."""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

UNITS_NOTE = "Lengths are in meters (assumed; the dataset does not state units)."


def build_summary(
    *,
    optimizer: str,
    optimizer_params: dict,
    n_left: int,
    n_right: int,
    center_length_m: float,
    line_length_m: float,
    alpha: np.ndarray,
    stage_times_ms: dict,
) -> dict:
    """Collect the facts of one run into a JSON-friendly dict."""
    # float(...) turns NumPy numbers into plain Python floats, which json can write.
    alpha_range = {"min": float(alpha.min()), "max": float(alpha.max())}

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "optimizer": optimizer,
        "optimizer_params": optimizer_params,
        "points": {"left": n_left, "right": n_right},
        "lengths_m": {
            "centerline": round(center_length_m, 3),
            "racing_line": round(line_length_m, 3),
            "saving": round(center_length_m - line_length_m, 3),
        },
        "alpha_range": alpha_range,
        "stage_times_ms": {name: round(ms, 3) for name, ms in stage_times_ms.items()},
        "notes": UNITS_NOTE,
    }


def write_summary(summary: dict, path: Path) -> None:
    """Write `summary` as indented JSON, creating the folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")  # end the file with a newline
