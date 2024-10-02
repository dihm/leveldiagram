"""
Miscellaneous utility functions
"""

import platform
from importlib.metadata import version
from collections.abc import Sequence
import re

from typing import Any

seq_contents = r"[\(|\[\{](.*)[\)|\]\}]"

def ket_str(s: Any) -> str:
    """
    Put a ket around the string in matplotlib.

    If input is a Sequence, but not a str or dict,
    the string representation will only show the container
    contents. For a tuple `(1,2)`, the resulting ket
    will have the form :math:`|1,2\\rangle`.

    Parameters:
        s: Object to be converted to string and placed inside a ket.

    Returns:
        str: A string that will render as :math:`\\left|\\text{s}\\right\\rangle`
    """

    in_s = str(s)

    if not isinstance(s, str) and isinstance(s, Sequence):
        # if sequence, but not string or dict, drop brackets in display
        # use regex to handle more complex things like namedtuples
        in_s = re.search(seq_contents, in_s).group(1)

    out_s = "$\\left|" + in_s + "\\right\\rangle$"

    return out_s


def bra_str(s: Any) -> str:
    """
    Put a bra around the string in matplotlib.

    If input is a Sequence, but not a str or dict,
    the string representation will only show the container
    contents. For a tuple `(1,2)`, the resulting bra
    will have the form :math:`\\langle1,2|`.

    Parameters:
        s: Object to be converted to a string and placed inside a bra.

    Returns:
        str: A string that will render as :math:`\\left\\langle\\text{s}\\right|`
    """

    in_s = str(s)

    if not isinstance(s, str) and isinstance(s, Sequence):
        # if sequence, but not string or dict, drop brackets in display
        # use regex to handle more complex things like namedtuples
        in_s = re.search(seq_contents, in_s).group(1)

    out_s = "$\\left\\langle" + in_s + "\\right|$"

    return out_s


def deep_update(mapping: dict, *updating_mappings: dict) -> dict:
    """
    Helper function to update nested dictionaries.

    Lifted from `pydantic <https://github.com/pydantic/pydantic/blob/main/pydantic/_internal/_utils.py>`_

    Returns:
        dict: Deep-updated copy of `mapping`
    """
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def about():
    """
    Display version of leveldiagram and critical dependencies.
    """

    header = """
        leveldiagram
    ====================
    """
    print(header)
    print(f'leveldiagram Version: {version("leveldiagram"):s}')
    dep_header = """
        Dependencies
    ====================
    """
    print(dep_header)
    print(f'Python Version:       {platform.python_version():s}')
    print(f'NumPy Version:        {version("numpy"):s}')
    print(f'Matplotlib Version:   {version("matplotlib"):s}')
    print(f'NetworkX Version:     {version("networkx"):s}')
    