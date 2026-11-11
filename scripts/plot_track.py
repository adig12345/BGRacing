"""Plot the left and right track boundaries.

Run from the project root:  python -m scripts.plot_track
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to files only, no window (needed in Docker)
import matplotlib.pyplot as plt  # noqa: E402  (must come after use())
import numpy as np  # noqa: E402

from src.geometry import load_track  # noqa: E402

CSV_PATH = Path("data/BrandsHatchLayout.csv")
OUTPUT_PATH = Path("output/track_boundaries.png")
FIGURE_SIZE = (10, 10)  # inches; the track is roughly square
LEFT_COLOR = "blue"
RIGHT_COLOR = "red"


def main() -> None:
    track = load_track(CSV_PATH)
    # The CSV does not repeat the first point at the end, so repeat it here
    # to draw the closing segment (last point -> first point) of each loop.
    left = np.concatenate([track.left, track.left[:1]])
    right = np.concatenate([track.right, track.right[:1]])

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    ax.plot(left[:, 0], left[:, 1], color=LEFT_COLOR, label="Left boundary")
    ax.plot(right[:, 0], right[:, 1], color=RIGHT_COLOR, label="Right boundary")

    ax.set_aspect("equal")
    ax.set_title("Brands Hatch Track Boundaries")
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    ax.legend()
    ax.grid(True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
