"""Plot the left and right track boundaries.

Run from the project root:  python -m scripts.plot_track
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to files only, no window (needed in Docker)
import matplotlib.pyplot as plt  # noqa: E402  (must come after use())

from src.geometry import load_track  # noqa: E402

CSV_PATH = Path("data/BrandsHatchLayout.csv")
OUTPUT_PATH = Path("output/track_boundaries.png")


def main() -> None:
    track = load_track(CSV_PATH)

    fig, ax = plt.subplots(figsize = (10, 10)) # TODO - size in config

    ax.plot (
        track.left[:, 0],
        track.left[:, 1],
        color = 'blue', # TODO - colors in config
        label='Left boundary'
    )
    ax.plot (
        track.right[:, 0],
        track.right[:, 1],
        color = 'red', # TODO - colors in config
        label='Right boundary'
    )
    

    ax.set_aspect('equal')
    ax.set_title('Brands Hatch Track Boundaries')
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.legend()
    ax.grid(True)
    # TODO - make sure in readme to write that i assumed meters, and units arn't givern

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
    plt.close(fig)


if __name__ == "__main__":
    main()
