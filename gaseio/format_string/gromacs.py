"""
format_string
"""
from collections import OrderedDict
import numpy as np
import parse

import atomtools.unit

from .. import ext_types
from .. import ext_methods


"""

http://manual.gromacs.org/documentation/5.1/user-guide/file-formats.html#gro



gro
Files with the gro file extension contain a molecular structure in Gromos87 format. gro files can be used as trajectory by simply concatenating files. An attempt will be made to read a time value from the title string in each frame, which should be preceded by ‘t=‘, as in the sample below.

A sample piece is included below:

MD of 2 waters, t= 0.0
    6
    1WATER  OW1    1   0.126   1.624   1.679  0.1227 -0.0580  0.0434
    1WATER  HW2    2   0.190   1.661   1.747  0.8085  0.3191 -0.7791
    1WATER  HW3    3   0.177   1.568   1.613 -0.9045 -2.6469  1.3180
    2WATER  OW1    4   1.275   0.053   0.622  0.2519  0.3140 -0.1734
    2WATER  HW2    5   1.337   0.002   0.680 -1.0641 -1.1349  0.0257
    2WATER  HW3    6   1.326   0.120   0.568  1.9427 -0.8216 -0.0244
   1.82060   1.82060   1.82060
Lines contain the following information (top to bottom):

title string (free format string, optional time in ps after ‘t=‘)
number of atoms (free format integer)
one line for each atom (fixed format, see below)
box vectors (free format, space separated reals), values: v1(x) v2(y) v3(z) v1(y) v1(z) v2(x) v2(z) v3(x) v3(y), the last 6 values may be omitted (they will be set to zero). GROMACS only supports boxes with v1(y)=v1(z)=v2(z)=0.
This format is fixed, ie. all columns are in a fixed position. Optionally (for now only yet with trjconv) you can write gro files with any number of decimal places, the format will then be n+5 positions with n decimal places (n+1 for velocities) in stead of 8 with 3 (with 4 for velocities). Upon reading, the precision will be inferred from the distance between the decimal points (which will be n+5). Columns contain the following information (from left to right):

residue number (5 positions, integer)
residue name (5 characters)
atom name (5 characters)
atom number (5 positions, integer)
position (in nm, x y z in 3 columns, each 8 positions with 3 decimal places)
velocity (in nm/ps (or km/s), x y z in 3 columns, each 8 positions with 4 decimal places)
Note that separate molecules or ions (e.g. water or Cl-) are regarded as residues. If you want to write such a file in your own program without using the GROMACS libraries you can use the following formats:

C format
"%5d%-5s%5s%5d%8.3f%8.3f%8.3f%8.4f%8.4f%8.4f"
Fortran format
(i5,2a5,i5,3f8.3,3f8.4)
Pascal format
This is left as an exercise for the user
Note that this is the format for writing, as in the above example fields may be written without spaces, and therefore can not be read with the same format statement in C.




"""

GROMACS_FORMAT_STRING = "{:5d}{:<5S}{:5S}{:5d}{:8.3f}{:8.3f}{:8.3f}"
GROMACS_FORMAT_STRING_WITH_VELOCITY = "{:5d}{:<5S}{:5S}{:5d}{:8.3f}{:8.3f}{:8.3f}{:8.4f}{:8.4f}{:8.4f}"


GROMACS_COL_SPECIFICATION = [5, 5, 5, 5, 8, 8, 8, 8, 8, 8]
GROMACS_COL_SPECIFICATION = [[sum(GROMACS_COL_SPECIFICATION[:i]), sum(
    GROMACS_COL_SPECIFICATION[:i+1])] for i in range(len(GROMACS_COL_SPECIFICATION))]
# print(GROMACS_COL_SPECIFICATION)


bonds_items = ['ai', 'aj', 'funct', 'c0', 'c1']
pairs_items = ['ai', 'aj', 'funct', 'c0', 'c1']
angles_items = ['ai', 'aj', 'ak', 'funct', 'c0', 'c1']
dihedrals_items = ['ai', 'aj', 'ak', 'al', 'funct', 'c0', 'c1', 'c2']
inversion_dihedrals_items = ['ai', 'aj', 'ak', 'al', 'funct', 'c0', 'c1']


def itp_postprocess(arrays):
    if not 'bonds' in arrays:
        arrays['bonds'] = dict(zip(bonds_items,
                                   [list() for _ in range(len(bonds_items))]))
    if not 'pairs' in arrays:
        arrays['pairs'] = dict(zip(pairs_items,
                                   [list() for _ in range(len(pairs_items))]))
    if not 'angles' in arrays:
        arrays['angles'] = dict(zip(angles_items,
                                    [list() for _ in range(len(angles_items))]))
    if not 'dihedrals' in arrays:
        arrays['dihedrals'] = dict(
            zip(dihedrals_items, [list() for _ in range(len(dihedrals_items))]))
    if not 'inversion_dihedrals' in arrays:
        arrays['inversion_dihedrals'] = dict(zip(inversion_dihedrals_items, [
                                             list() for _ in range(len(inversion_dihedrals_items))]))


FORMAT_STRING = {
    'gromacs': {
        'primitive_data': OrderedDict({
            r'^\s*(.*)\n.*\n[\s\S]*': {
                'important': True,
                'selection': 0,
                'key': 'comments',
                'type': str,
            },
            r'^\s*.*t\s*=\s*(\d+[\.\d]*)\n.*\n[\s\S]*': {
                # 'debug' : True,
                'important': False,
                'selection': 0,
                'key': 'frame_time',
                'type': float,
                'process': lambda data, arrays: float(data) * atomtools.unit.trans_time('ps'),
            },
            r'^.*\n\s*\d+\n([\s\S]*?)\n[0-9\. ]*$': {
                # 'debug' : True,
                'important': True,
                'selection': -1,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy_fixed_width(data, \
                                                                                           colspecs=GROMACS_COL_SPECIFICATION, header=None, \
                                                                                           nan_fill=None),
                'key': [
                    {
                        'key': 'funct',
                        'type': int,
                        'index': ':,0',
                    },
                    {
                        'key': 'residue_name',
                        'type': str,
                        'index': ':,1',
                    },
                    {
                        'key': 'customized_symbols',
                        'type': str,
                        'index': ':,2',
                    },
                    {
                        'key': 'gro_atom_number',
                        'type': int,
                        'index': ':,3',
                    },
                    {
                        'key': 'positions',
                        'type': float,
                        'index': ':,4:7',
                        'process': lambda data, arrays: data * atomtools.unit.trans_length('nm', 'Ang'),
                    },
                    {
                        'key': 'velocities',
                        'type': float,
                        'index': ':,7:10',
                        'process': lambda data, arrays: None if (data == None).all \
                        else data * atomtools.unit.trans_velocity('nm/ps', 'Ang/fs'),
                    },
                ],
            },
            r'^.*\n\s*\d+\n[\s\S]*?\n([0-9\. ]*)\n*$': {
                'important': True,
                'selection': 0,
                'process': lambda data, arrays: ext_methods.regularize_cell(ext_methods.datablock_to_numpy(data)),
                'key': 'cell',
                'type': float,
            },
        }),
        'synthesized_data': OrderedDict({
        }),
        'multiframe': True,
        'frame_spliter': r'[^\n].*\n\s*\d+\s*\n[\s\S]*?\n\s*[0-9\.]+\s+[0-9\.]+\s+[0-9\.]+[\s\.0-9]*',
    },
    'gromacs-top': {
        'ignorance': (';', '<'),
        'non_regularize': True,
        'primitive_data': OrderedDict({
            r'\[\s*atomtypes\s*\]\n([\s\S]*?)\n[\n<]': {
                'important': False,
                'selection': 0,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data).reshape((-1, 7)),
                'key': [
                    {
                        'key': 'atomtypes/name1',
                        'type': str,
                        'index': ':,0',
                    },
                    {
                        'key': 'atomtypes/name2',
                        'type': str,
                        'index': ':,1',
                    },
                    {
                        'key': 'atomtypes/mass',
                        'type': float,
                        'index': ':,2',
                    },
                    {
                        'key': 'atomtypes/charge',
                        'type': float,
                        'index': ':,3',
                    },
                    {
                        'key': 'atomtypes/ptype',
                        'type': str,
                        'index': ':,4',
                    },
                    {
                        'key': 'atomtypes/sigma',
                        'type': float,
                        'index': ':,5',
                    },
                    {
                        'key': 'atomtypes/epsilon',
                        'type': float,
                        'index': ':,6',
                    },
                ],
            },
            r'\[\s*system\s*\]\n([\s\S]*?)\n[\n<]': {
                'important': False,
                'selection': -1,
                'key': 'system',
                'type': str,
            },
            r'\[\s*atoms\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                'important': False,
                'selection': 0,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'atoms/number',
                        'type': int,
                        'index': ':,0',
                    },
                    {
                        'key': 'atoms/type',
                        'type': str,
                        'index': ':,1',
                    },
                    {
                        'key': 'atoms/residue_number',
                        'type': int,
                        'index': ':,2',
                    },
                    {
                        'key': 'atoms/residue',
                        'type': str,
                        'index': ':,3',
                    },
                    {
                        'key': 'atoms/atom',
                        'type': str,
                        'index': ':,4',
                    },
                    {
                        'key': 'atoms/cgnr',
                        'type': int,
                        'index': ':,5',
                    },
                    {
                        'key': 'atoms/charge',
                        'type': float,
                        'index': ':,6',
                    },
                    {
                        'key': 'atoms/mass',
                        'type': float,
                        'index': ':,7',
                    },
                ],
            },
            r'\[\s*bonds\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                'important': False,
                'selection': 0,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'bonds/ai',
                        'type': int,
                        'index': ':,0',
                    },
                    {
                        'key': 'bonds/aj',
                        'type': int,
                        'index': ':,1',
                    },
                    {
                        'key': 'bonds/funct',
                        'type': int,
                        'index': ':,2',
                    },
                    {
                        'key': 'bonds/c0',
                        'type': float,
                        'index': ':,3',
                    },
                    {
                        'key': 'bonds/c1',
                        'type': float,
                        'index': ':,4',
                    },
                ],
            },
            r'\[\s*angles\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                # 'debug': True,
                'important': False,
                'selection': 0,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'angles/ai',
                        'type': int,
                        'index': ':,0',
                    },
                    {
                        'key': 'angles/aj',
                        'type': int,
                        'index': ':,1',
                    },
                    {
                        'key': 'angles/ak',
                        'type': int,
                        'index': ':,2',
                    },
                    {
                        'key': 'angles/funct',
                        'type': int,
                        'index': ':,3',
                    },
                    {
                        'key': 'angles/c0',
                        'type': float,
                        'index': ':,4',
                    },
                    {
                        'key': 'angles/c1',
                        'type': float,
                        'index': ':,5',
                    },
                ],
            },
            r'\[\s*dihedrals\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                # 'debug' : True,
                'important': False,
                'selection': 0,
                'join': '\n',
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'dihedrals/ai',
                        'type': int,
                        'index': ':,0',
                    },
                    {
                        'key': 'dihedrals/aj',
                        'type': int,
                        'index': ':,1',
                    },
                    {
                        'key': 'dihedrals/ak',
                        'type': int,
                        'index': ':,2',
                    },
                    {
                        'key': 'dihedrals/al',
                        'type': int,
                        'index': ':,3',
                    },
                    {
                        'key': 'dihedrals/funct',
                        'type': int,
                        'index': ':,4',
                    },
                    {
                        'key': 'dihedrals/c0',
                        'type': float,
                        'index': ':,5',
                    },
                    {
                        'key': 'dihedrals/c1',
                        'type': float,
                        'index': ':,6',
                    },
                    {
                        'key': 'dihedrals/c2',
                        'type': float,
                        'index': ':,7',
                    },
                ],
            },
            r"\[ dihedrals \][\s\S]+?\n\n\[ dihedrals \](.+[\s\S]+)$": {
                # 'debug' : True,
                'important': False,
                'selection': 0,
                'join': '\n',
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'inversion_dihedrals/ai',
                        'type': int,
                        'index': ':,0',
                    },
                    {
                        'key': 'inversion_dihedrals/aj',
                        'type': int,
                        'index': ':,1',
                    },
                    {
                        'key': 'inversion_dihedrals/ak',
                        'type': int,
                        'index': ':,2',
                    },
                    {
                        'key': 'inversion_dihedrals/al',
                        'type': int,
                        'index': ':,3',
                    },
                    {
                        'key': 'inversion_dihedrals/funct',
                        'type': int,
                        'index': ':,4',
                    },
                    {
                        'key': 'inversion_dihedrals/c0',
                        'type': float,
                        'index': ':,5',
                    },
                    {
                        'key': 'inversion_dihedrals/c1',
                        'type': float,
                        'index': ':,6',
                    },
                ],
            },
        }),
        'synthesized_data': OrderedDict({
        }),
        'postprocess': itp_postprocess,
    },

}
