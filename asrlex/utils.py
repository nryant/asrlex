"""Utility functions."""
from numbers import Integral
import os
from pathlib import Path

__all__ = ['validate_integer_arg', 'validate_ranged_arg', 'which', 'xor']


def validate_integer_arg(x, name, min_val=None, max_val=None):
    """Validate integer argument to function.

    Raises
    ------
    TypeError
        Raised of ``x`` is not an Integral type.

    ValueError:
        Raised if ``x<min_val`` or ``x>max_val``.
    """
    if not isinstance(x, Integral):
        raise TypeError(
            '%s must be integer; received %s' % (name, type(x)))
    validate_ranged_arg(x, name, min_val, max_val)


def validate_ranged_arg(x, name, min_val=None, max_val=None):
    """Validate ranged argument to function.

    Raises
    ------
    ValueError:
        Raised if ``x<min_val`` or ``x>max_val``.
    """
    if (min_val is not None and max_val is not None and
        not min_val <= x <= max_val):
        raise ValueError(
            '%s must be in range [%d, %d]; received %d' %
            (name, min_val, max_val, x))
    if min_val is not None and x < min_val:
        raise ValueError(
            '%s must be >=%d; received %d' % (name, min_val, x))
    if max_val is not None and x > max_val:
        raise ValueError(
            '%s must be <=%d; received %d' % (name, max_val, x))


def which(program, search_dirs=None):
    """Returns path to excutable ``program``.

    If ``program`` is not found on the user's PATH, returns ``None``.

    Parameters
    ----------
    program : str
        Name of program to search for.

    search_dirs : iterable of Path, optional
        List of additional directories to search. These directories will be
        searched in order **BEFORE** the user's PATH.
        (Default: None)
    """
    def is_exe(fpath):
        return fpath.is_file() and os.access(fpath, os.X_OK)
    program = Path(program)
    if search_dirs is None:
        search_dirs = []
    search_dirs = list(search_dirs)
    search_dirs += os.environ['PATH'].split(os.pathsep)
    if is_exe(program):
        return program
    for dirpath in search_dirs:
        fpath = Path(dirpath, program)
        if is_exe(fpath):
            return fpath
    return None


def xor(*args):
    """Return True if exactly one of inputs evaluates as True."""
    return sum(map(bool, args)) == 1
