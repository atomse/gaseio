"""
format_string
"""
from collections import OrderedDict
import numpy as np
import parse
import atomtools

from .. import ext_types
from .. import ext_methods


GROMACS_FORMAT_STRING = "{:5d}{:<5S}{:5S}{:5d}{:8.3f}{:8.3f}{:8.3f}"
GROMACS_FORMAT_STRING_WITH_VELOCITY = "{:5d}{:<5S}{:5S}{:5d}{:8.3f}{:8.3f}{:8.3f}{:8.4f}{:8.4f}{:8.4f}"

FORMAT_STRING = {
    'gromacs': {
        'primitive_data'  : OrderedDict({
            r'^\s*(.*)\n.*\n[\s\S]*': {
                'important': True,
                'selection' : 0,
                'key' : 'comments',
                'type' : str,
            },
            r'^\s*.*t\s*=\s*(\d+[\.\d]*)\n.*\n[\s\S]*': {
                # 'debug' : True,
                'important': False,
                'selection' : 0,
                'key' : 'frame_time',
                'type' : float,
                'process' : lambda data, arrays: float(data) * atomtools.unit.trans_time('ps'),
            },
            r'^.*\n\s*\d+\n([\s\S]*?)\n[0-9\. ]*$':{
                # 'debug' : True,
                'important': True,
                'selection' : -1,
                'process' : lambda data, arrays: np.array([list(parse.parse(GROMACS_FORMAT_STRING_WITH_VELOCITY, line) or \
                                                                parse.parse(GROMACS_FORMAT_STRING, line))\
                                                           for line in data.split('\n')]),
                'key' : [
                    {
                        'key' : 'residue_number',
                        'type' : int,
                        'index' : ':,0',
                    },
                    {
                        'key' : 'residue_name',
                        'type' : str,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'customized_symbols',
                        'type' : str,
                        'index' : ':,2',
                    },
                    {
                        'key' : 'gro_atom_number',
                        'type' : int,
                        'index' : ':,3',
                    },
                    {
                        'key' : 'positions',
                        'type' : float,
                        'index' : ':,4:7',
                        'process' : lambda data, arrays: data * atomtools.unit.trans_length('nm', 'Ang'),
                    },
                    {
                        'key' : 'velocities',
                        'type' : float,
                        'index' : ':,7:10',
                        'process' : lambda data, arrays: data * atomtools.unit.trans_velocity('nm/ps', 'Ang/fs'),
                    },
                    ],
            },
            r'^.*\n\s*\d+\n[\s\S]*?\n([0-9\. ]*)\n*$':{
                'important': True,
                'selection' : 0,
                'process' : lambda data, arrays: ext_methods.regularize_cell(ext_methods.datablock_to_numpy(data)),
                'key' : 'cell',
                'type' : float,
            },
        }),
        'synthesized_data' : OrderedDict({
        }),
        'multiframe' : True,
        'frame_spliter' : r'[^\n].*\n\s*\d+\s*\n[\s\S]*?\n\s*[0-9\.]+\s+[0-9\.]+\s+[0-9\.]+[\s\.0-9]*',
    },
    'gromacs-top': {
        'ignorance' : (';','<'),
        'non_regularize' : True,
        'primitive_data'  : OrderedDict({
            r'\[\s*atomtypes\s*\]\n([\s\S]*?)\n[\n<]': {
                'important': False,
                'selection' : 0,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data).reshape((-1, 7)),
                'key' : [
                    {
                        'key' : 'atomtypes/name1',
                        'type' : str,
                        'index' : ':,0',
                    },
                    {
                        'key' : 'atomtypes/name2',
                        'type' : str,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'atomtypes/mass',
                        'type' : float,
                        'index' : ':,2',
                    },
                    {
                        'key' : 'atomtypes/charge',
                        'type' : float,
                        'index' : ':,3',
                    },
                    {
                        'key' : 'atomtypes/ptype',
                        'type' : str,
                        'index' : ':,4',
                    },
                    {
                        'key' : 'atomtypes/sigma',
                        'type' : float,
                        'index' : ':,5',
                    },
                    {
                        'key' : 'atomtypes/epsilon',
                        'type' : float,
                        'index' : ':,6',
                    },
                ],
            },
            r'\[\s*system\s*\]\n([\s\S]*?)\n[\n<]': {
                'important': False,
                'selection' : -1,
                'key' : 'system',
                'type' : str,
            },
            r'\[\s*atoms\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                'important': False,
                'selection' : 0,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'atoms/number',
                        'type' : int,
                        'index' : ':,0',
                    },
                    {
                        'key' : 'atoms/type',
                        'type' : str,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'atoms/residue_number',
                        'type' : int,
                        'index' : ':,2',
                    },
                    {
                        'key' : 'atoms/residue',
                        'type' : str,
                        'index' : ':,3',
                    },
                    {
                        'key' : 'atoms/atom',
                        'type' : str,
                        'index' : ':,4',
                    },
                    {
                        'key' : 'atoms/cgnr',
                        'type' : int,
                        'index' : ':,5',
                    },
                    {
                        'key' : 'atoms/charge',
                        'type' : float,
                        'index' : ':,6',
                    },
                    {
                        'key' : 'atoms/mass',
                        'type' : float,
                        'index' : ':,7',
                    },
                ],
            },
            r'\[\s*bonds\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                'important' : False,
                'selection' : 0,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'bonds/number1',
                        'type' : int,
                        'index' : ':,0',
                    },
                    {
                        'key' : 'bonds/number2',
                        'type' : int,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'bonds/residue_number',
                        'type' : int,
                        'index' : ':,2',
                    },
                    {
                        'key' : 'bonds/bond_length',
                        'type' : float,
                        'index' : ':,3',
                    },
                    {
                        'key' : 'bonds/bond_force',
                        'type' : float,
                        'index' : ':,4',
                    },
                ],
            },
            r'\[\s*angles\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                'important': False,
                'selection' : 0,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'angles/number1',
                        'type' : int,
                        'index' : ':,0',
                    },
                    {
                        'key' : 'angles/number2',
                        'type' : int,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'angles/number3',
                        'type' : int,
                        'index' : ':,2',
                    },
                    {
                        'key' : 'angles/residue_number',
                        'type' : int,
                        'index' : ':,3',
                    },
                    {
                        'key' : 'angles/eq_angle',
                        'type' : float,
                        'index' : ':,4',
                    },
                    {
                        'key' : 'angles/angle_force',
                        'type' : float,
                        'index' : ':,5',
                    },
                ],
            },
            r'\[\s*dihedrals\s*\]\n(.+[\s\S]*?)\n[\n<]': {
                # 'debug' : True,
                'important': False,
                'selection' : 0,
                'join' : '\n',
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'dihedrals/number1',
                        'type' : int,
                        'index' : ':,0',
                    },
                    {
                        'key' : 'dihedrals/number2',
                        'type' : int,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'dihedrals/number3',
                        'type' : int,
                        'index' : ':,2',
                    },
                    {
                        'key' : 'dihedrals/number4',
                        'type' : int,
                        'index' : ':,3',
                    },
                    {
                        'key' : 'dihedrals/residue_number',
                        'type' : int,
                        'index' : ':,4',
                    },
                    {
                        'key' : 'dihedrals/eq_dihedral',
                        'type' : float,
                        'index' : ':,5',
                    },
                    {
                        'key' : 'dihedrals/dihedral_force',
                        'type' : float,
                        'index' : ':,6',
                    },
                ],
            },
        }),
        'synthesized_data' : OrderedDict({
        }),
    },

}
