"""
format_string
"""



import re
from collections import OrderedDict
import atomtools

from .. import ext_types
from .. import ext_methods
from ..format_parser import read

FORMAT_STRING = {
    'cp2k': {
        'calculator': 'CP2K',
        # 'ignorance' : r'\s*#.*\n',
        'ignorance' : ('#',),
        'primitive_data' : {
            r'&COORD\s*\n([\s\S]*?)\n\s*&END' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'symbols',
                        'type' : str,
                        'index' : ':,0',
                        'process' : lambda data, arrays: data.tolist(),
                    },
                    {
                        'key' : 'positions',
                        'type' : float,
                        'index' : ':,1:4',
                    },
                ]
                },
            r'&CELL[\s\S]*\n(\s*A\s+[\s\S]*?)&END' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'cell',
                        'type' : float,
                        'index' : ':,1:3',
                    },
                ],
                },
            },
        'synthesized_data' : OrderedDict({
            'positions' : {
                'prerequisite' : ['xyzfile'],
                'equation' : lambda arrays: read(arrays['xyzfile'], format='xyz')['positions']
                },
            'symbols' : {
                'prerequisite' : ['xyzfile'],
                'equation' : lambda arrays: read(arrays['xyzfile'], format='xyz')['symbols']
                },
            }),
    },
    'cp2k-out': {
        'calculator': 'CP2K',
        'primitive_data': {
            r'ATOMIC COORDINATES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n{2,}' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'numbers',
                        'index' : ':,3',
                        'type' : int,
                    },
                    {
                        'key' : 'positions',
                        'index' : ':,4:7',
                        'type' : float,
                    },
                    {
                        'key' : 'Zeff',
                        'index' : ':7',
                        'type' : float,
                    },
                    {
                        'key' : 'mass',
                        'index' : ':8',
                        'type' : float,
                    },
                ],
            },
            re.compile(r'ATOMIC COORDINATES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n{2,}') : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'all_positions',
                        'index' : ':,4:7',
                        'type' : float,
                    },
                ],
            },
            r'ATOMIC FORCES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n.*SUM OF ATOMIC FORCES' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'forces',
                        'index' : ':,3:6',
                        'type' : float,
                        'process' : lambda data, arrays: data * atomtools.unit.trans_force('au')
                    },
                ],
            },
            re.compile(r'ATOMIC FORCES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n.*SUM OF ATOMIC FORCES') : {
                'important' : True,
                'selection' : 'all',
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'all_forces',
                        'index' : ':,3:6',
                        'type' : float,
                        'process' : lambda data, arrays: data * atomtools.unit.trans_force('au')
                    },
                ],
            },
            r'ENERGY\| Total FORCE_EVAL.*\s{2,}([+-]\d+.*)\n' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/potential_energy',
                'type' : float,
                'process' : lambda data, arrays: data * atomtools.unit.trans_energy('au', 'eV'),
            },
            re.compile(r'ENERGY\| Total FORCE_EVAL.*\s{2,}([+-]\d+.*)\n') : {
                'important' : False,
                'selection' : 'all',
                'key' : 'calc_arrays/all_potential_energy',
                'type' : float,
                'process' : lambda data, arrays: data * atomtools.unit.trans_energy('au', 'eV'),
            },
            r'GEOMETRY OPTIMIZATION COMPLETED' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/geo_opt_done',
                'process' : lambda data, arrays: True if data else False,
            },
            },
        'synthesized_data' : OrderedDict({
            }),
    },
}
