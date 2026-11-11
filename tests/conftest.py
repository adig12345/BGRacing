"""Shared test data. pytest loads this file automatically; no import needed."""

import numpy as np
import pytest


@pytest.fixture
def outer_square() -> np.ndarray:
    """Outer corners of two concentric squares, at +-3."""
    return np.array([[-3, -3], [3, -3], [3, 3], [-3, 3]], dtype=float)


@pytest.fixture
def inner_square() -> np.ndarray:
    """Inner corners of two concentric squares, at +-1."""
    return np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], dtype=float)
