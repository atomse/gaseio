"""
format_string
"""


import os

from collections import OrderedDict
import atomtools.unit

from .. import ext_types
from .. import ext_methods
from ..format_parser import read

FORMAT_STRING = {
    'castep': {
        'calculator': 'CASTEP',
        # 'ignorance' : r'\s*#.*\n',
        'ignorance' : ('#',),
        'primitive_data' : {
            r'%max_core\s+(\d+)\s*\n' : {
                'important': False,
                'selection' : -1,
                'type': int,
                'key' : 'max_core',
                },
            r'%max_memory(\d+.*)\s*\n' : {
                'important': False,
                'selection' : -1,
                'type': str,
                'key' : 'max_memory',
                },
            # r'!\s*([\s\S]*?)\n' : {
            #     'important': True,
            #     'selection' : -1,
            #     'type': str,
            #     'key' : 'calc_arrays/command',
            #     },
            r'#\s*comments\s*([\s\S]*?)\n' : {
                # 'debug' : True,
                'important' : False,
                'selection' : -1,
                'type' : str,
                'join' : '\n',
                'key' : 'comments',
                },
            r'\n!\s*(.*)' : {
                # 'debug' : True,
                'important' : True,
                'selection' : -1,
                'type' : str,
                'join' : ' ',
                'key' : 'calc_arrays/command',
            },
            r'[\s\S]*?xyz.*\s+(\d+)\s+\d+[\s\S]*?' : {
                'important' : True,
                'selection' : -1,
                'type' : int,
                'key' : 'charge'
                },
            r'[\s\S]*?xyz.*\s+\d+\s+(\d+)[\s\S]*?' : {
                'important' : True,
                'selection' : -1,
                'type' : int,
                'key' : 'multiplicity'
                },
            r'\*\s*xyzfile\s+\d+\s+\d+\s+(.+)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : str,
                'key' : 'xyzfile',
                'process' : lambda data, arrays: os.path.join(arrays['basedir'], data),
                },
            r'\*\s*xyz\s+\d+\s+\d+\s+([\s\S]*?)\*' : {
                'important' : False,
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
            r'%basis([\s\S]*?)\n\s*end' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'basis_symbols',
                        'type' : str,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'basis_types',
                        'type' : str,
                        'index' : ':,2',
                    },
                ],
                },
            # r'#\s*[\s\S]*?\n\n.*\n\n.*-?\d+\s*\d+\s*\n[\s\S]*?\n\n([\s\S])' : {
            #         'important' : True,
            #         'selection' : -1,
            #         'type' : str,
            #         'key' : 'calc_arrays/appendix'
            #     },
            # r'#[\s\S]*?connectivity[\s\S]*?\n\n[\s\S]*?\n\s*\n\s*([\d\n\. ]*)\n\n':{
            #         'important': False,
            #         'selection' : -1,
            #         'type' : str,
            #         'key' : 'calc_arrays/connectivity',
            #     },
            # r'#[\s\S]*?gen[\s\S]*?\n\n[\s\S]*?\n\s*\n\s*[\d\n\. ]*\n\n([A-Z][a-z]?[\s\S]*?\n\n[A-Z][a-z]?.*\d\n[\s\S]*?)\n\n':{
            #         'important': False,
            #         'selection' : -1,
            #         'type' : str,
            #         'key' : 'calc_arrays/genecp',
            #     },
            # r'(\$NBO.*\$END)':{
            #         'important': False,
            #         'selection' : -1,
            #         'type' : str,
            #         'key' : 'calc_arrays/nbo',
            #     },
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
    'castep-out': {
        'calculator': 'CASTEP',
        'primitive_data': {
            r'ATOMIC COORDINATES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n{2,}' : {
                'important' : True,
                'selection' : -1,
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
            r'ATOMIC FORCES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n.*SUM OF ATOMIC FORCES' : {
                'important' : True,
                'selection' : -1,
                'key' : [
                    {
                        'key' : 'forces',
                        'index' : ':,3:6',
                        'type' : float,
                        'process' : lambda data, arrays: data * atomtools.unit.trans_force('au')
                    },
                ],
            },
            r'ATOMIC FORCES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n.*SUM OF ATOMIC FORCES' : {
                'important' : True,
                'selection' : 'all',
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
            r'ENERGY\| Total FORCE_EVAL.*\s{2,}([+-]\d+.*)\n' : {
                'important' : False,
                'selection' : 'all',
                'key' : 'calc_arrays/all_potential_energy',
                'type' : float,
                'process' : lambda data, arrays: data * atomtools.unit.trans_energy('au', 'eV'),
            },
            r'GEOMETRY OPTIMIZATION COMPLETED' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/geometry_opt_done',
            },
            },
        'synthesized_data' : OrderedDict({
            }),
    },
}
