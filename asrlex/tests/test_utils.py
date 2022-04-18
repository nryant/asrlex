"""Tests for utility functions."""
import pytest

from asrlex.utils import validate_integer_arg, validate_ranged_arg, xor


def test_validate_integer_arg():
    with pytest.raises(TypeError):
        validate_integer_arg(1.1, 'x')
    with pytest.raises(TypeError):
        validate_integer_arg('1', 'x')
    with pytest.raises(ValueError):
        validate_integer_arg(1, 'x', min_val=2)
    with pytest.raises(ValueError):
        validate_integer_arg(1, 'x', max_val=0)
    with pytest.raises(ValueError):
        validate_integer_arg(-1, 'x', min_val=0, max_val=2)
    with pytest.raises(ValueError):
        validate_integer_arg(3, 'x', min_val=0, max_val=2)


def test_validate_ranged_arg():
    with pytest.raises(ValueError):
        validate_integer_arg(1, 'x', min_val=2.1)
    with pytest.raises(ValueError):
        validate_integer_arg(1, 'x', max_val=0.3)
    with pytest.raises(ValueError):
        validate_integer_arg(-1, 'x', min_val=0.3, max_val=2.1)
    with pytest.raises(ValueError):
        validate_integer_arg(3, 'x', min_val=0.3, max_val=2.1)


def test_xor():
    assert xor(True, False)
    assert xor(False, False, True)
    assert xor(False, False, 1)
    assert not xor(False, False)
    assert not xor(True, True, False)
