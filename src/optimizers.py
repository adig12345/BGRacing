"""Racing-line optimizers. Pure NumPy, no ROS imports.

Every optimizer has the signature  optimizer(corridor, params) -> alpha
and returns one lateral offset per point (see geometry.Corridor for the
convention: 0 = centerline, +1 = left boundary, -1 = right boundary).
"""

from typing import Callable, Dict

import numpy as np

from src.geometry import Corridor

Optimizer = Callable[[Corridor, dict], np.ndarray]

OPTIMIZERS: Dict[str, Optimizer] = {}


def register(name: str) -> Callable[[Optimizer], Optimizer]:
    """Decorator: store the function in OPTIMIZERS under `name`."""

    def decorator(func: Optimizer) -> Optimizer:
        if name in OPTIMIZERS:
            raise ValueError(f"Optimizer '{name}' is already registered")
        OPTIMIZERS[name] = func
        return func

    return decorator


def get_optimizer(name: str) -> Optimizer:
    """Look up an optimizer by name, with a helpful error if it is unknown."""
    try:
        return OPTIMIZERS[name]
    except KeyError:
        raise ValueError(
            f"Unknown optimizer '{name}'. Available: {sorted(OPTIMIZERS)}"
        ) from None


@register("centerline")
def centerline(corridor: Corridor, params: dict) -> np.ndarray:
    """Baseline: stay on the centerline (alpha = 0 everywhere)."""
    return np.zeros(len(corridor.center))


@register("min_distance")
def min_distance(corridor: Corridor, params: dict) -> np.ndarray:
    """Shortest line that stays inside the corridor.

    Minimizes the sum of squared segment lengths (a QP) with a sweep solver:
    each point in turn moves to its best position given its two neighbours,
    clipped to +-alpha_limit. Sweeps repeat until nothing moves more than
    `tolerance`, or `max_iterations` sweeps were done.

    params: alpha_limit, max_iterations, tolerance.
    """
    alpha_limit = params["alpha_limit"]
    max_iterations = params["max_iterations"]
    tolerance = params["tolerance"]

    c, d = corridor.center, corridor.lateral
    n = len(c)
    dd = (d * d).sum(axis=1)  # d_i . d_i for every point (squared half-width)

    alpha = np.zeros(n)
    r = c.copy()  # current line points; kept up to date inside the sweep

    for _ in range(max_iterations):
        biggest_change = 0.0
        for i in range(n):
            prev, nxt = (i - 1) % n, (i + 1) % n  # wrap around the loop
            # Best alpha_i if there were no limits (solves the equation
            # d_i . (2*c_i + 2*alpha_i*d_i - r_prev - r_next) = 0 for alpha_i).
            best = d[i] @ (r[prev] + r[nxt] - 2 * c[i]) / (2 * dd[i])
            new_alpha = float(np.clip(best, -alpha_limit, alpha_limit))
            biggest_change = max(biggest_change, abs(new_alpha - alpha[i]))
            alpha[i] = new_alpha
            r[i] = c[i] + new_alpha * d[i]
        if biggest_change < tolerance:
            break

    return alpha
