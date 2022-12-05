"""
Miscellaneous utility functions
"""


def ket_str(s):
    """
    Put a ket around the string in matplotlib.

    Returns
    -------
    str
        A string that will render as :math:`\\left|\\text{s}\\right\\rangle`
    """

    in_s = str(s)

    out_s = '$\\left|' + in_s + '\\right\\rangle$'

    return out_s


def bra_str(s):
    """
    Put a bra around the string in matplotlib.

    Returns
    -------
    str
        A string that will render as :math:`\\left\\langle\\text{s}\\right|`
    """

    in_s = str(s)

    out_s = '$\\left\\langle' + in_s + '\\right|$'

    return out_s


def deep_update(mapping, *updating_mappings):
    """
    Helper function to update nested dictionaries.

    Lifted from pydantic

    Returns
    -------
    dict
        Deep-updated copy of `mapping`
    """
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping