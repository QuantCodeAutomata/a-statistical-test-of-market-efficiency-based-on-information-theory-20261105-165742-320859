"""Unit tests of the Theorem 2 error bound (src/error_bound.py)."""

import numpy as np
import pytest

from src.error_bound import lah_number, theorem2_bound


def test_lah_numbers_L4():
    assert lah_number(4, 1) == 24
    assert lah_number(4, 2) == 36
    assert lah_number(4, 3) == 12
    assert lah_number(4, 4) == 1


def test_lah_number_rejects_invalid_l():
    with pytest.raises(ValueError):
        lah_number(4, 0)
    with pytest.raises(ValueError):
        lah_number(4, 5)


def test_theorem2_bound_rejects_q_below_2():
    with pytest.raises(ValueError):
        theorem2_bound(1, 100)


def test_theorem2_bound_decreases_with_nj():
    nj = np.array([50, 100, 200, 400, 800])
    bound = theorem2_bound(2, nj)
    assert np.all(np.diff(bound) < 0)


def test_theorem2_bound_lower_q_is_tighter():
    """Lower q should give a lower (tighter) bound regardless of n_j
    (exp_4 research objective)."""
    nj = np.array([100, 500, 1000])
    b2 = theorem2_bound(2, nj)
    b3 = theorem2_bound(3, nj)
    b4 = theorem2_bound(4, nj)
    b5 = theorem2_bound(5, nj)
    assert np.all(b2 < b3)
    assert np.all(b3 < b4)
    assert np.all(b4 < b5)


def test_theorem2_bound_at_zero_is_infinite():
    bound = theorem2_bound(2, np.array([0]))
    assert np.isinf(bound[0])


def test_theorem2_bound_positive():
    nj = np.array([10, 100, 1000])
    for q in [2, 3, 4, 5]:
        assert np.all(theorem2_bound(q, nj) > 0)
