"""
unit
"""
from ase import units as ase_units


def unit_to_Ang(unit=None):
    if unit is None:
        return 1
    assert isinstance(unit, str), 'unit should be a string'
    unit = unit.lower()
    if 'ang' in unit:
        return 1
    if 'bohr' in unit or 'au' in unit:
        return ase_units.Bohr
    elif 'nm' in unit:
        return ase_units.nm
    elif 'pm' in unit:
        return ase_units.nm/1000
    else:
        raise NotImplementedError(unit, ' not valid')


