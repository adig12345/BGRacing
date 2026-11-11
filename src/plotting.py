"""Plot helpers. Pure matplotlib, no ROS imports."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files only, no window
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.geometry import Corridor, Track  # noqa: E402

# Colors from the validated reference palette (light surface).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"
BOUNDARY = "#898781"  # neutral gray: context, not a data series
RACING_LINE = "#2a78d6"  # categorical slot 1 (blue)
CENTERLINE = "#eb6834"  # categorical slot 2 (orange)


def _closed(points: np.ndarray) -> np.ndarray:
    """Return `points` with the first point repeated at the end (closed loop)."""
    return np.concatenate([points, points[:1]])


def _draw(ax: plt.Axes, points: np.ndarray, **style) -> None:
    """Draw a closed line through `points`; `style` goes to ax.plot."""
    closed = _closed(points)
    ax.plot(closed[:, 0], closed[:, 1], **style)


def save_result_plot(
    track: Track,
    corridor: Corridor,
    racing_line: np.ndarray,
    path: Path,
    title: str,
) -> None:
    """Save a PNG with the boundaries, centerline and racing line."""
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    # zorder = drawing order (higher is on top). The boundaries go on top of
    # the racing line so the line is visibly inside the road, never covering it.
    _draw(
        ax, corridor.center, color=CENTERLINE, linewidth=1.2, linestyle="--",
        label="Centerline", zorder=1,
    )
    _draw(
        ax, racing_line, color=RACING_LINE, linewidth=1.4, label="Racing line",
        zorder=2,
    )
    _draw(
        ax, track.left, color=BOUNDARY, linewidth=1.0, label="Track boundaries",
        zorder=3,
    )
    _draw(ax, track.right, color=BOUNDARY, linewidth=1.0, zorder=3)  # no label

    start = corridor.center[0]
    ax.plot(
        start[0], start[1], "o", color=INK, markersize=8,
        markeredgecolor=SURFACE, markeredgewidth=2, zorder=5,
        label="Start / finish (point 0)",
    )

    ax.set_aspect("equal")  # same scale on both axes, or the track is distorted
    ax.set_title(title, color=INK, fontsize=13)
    ax.set_xlabel("x [m] (assumed meters)", color=INK_SECONDARY)
    ax.set_ylabel("y [m] (assumed meters)", color=INK_SECONDARY)
    ax.tick_params(colors=INK_SECONDARY)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)  # grid behind the lines
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.legend(loc="best", frameon=True, facecolor=SURFACE, edgecolor=GRID)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)  # free the figure's memory
