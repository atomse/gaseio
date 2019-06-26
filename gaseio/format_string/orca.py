"""
format_string
"""


import os

from collections import OrderedDict
from .. import ext_types
from .. import ext_methods
from ..format_parser import read

FORMAT_STRING = {
    'orca': {
        'calculator': 'ORCA',
        'ignorance': ('#',),
        'primitive_data' : {
            r'%maxcore\s+(\d+)\s*\n' : {
                'important': False,
                'selection' : -1,
                'type': int,
                'key' : 'maxcore',
                },
            r'%maxmem(\d+.*)\s*\n' : {
                'important': False,
                'selection' : -1,
                'type': str,
                'key' : 'maxmem',
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
        # 'writer_formats': '%nproc={atoms.maxcore}\n%mem={atoms.maxmem}B\n%chk={randString()}.chk\n#p force b3lyp/6-31g(d)\n\ngase\n\n{atoms.charge} {atoms.multiplicity}\n{atoms.get_symbols_positions()}{atoms.calc.connectivity}{atoms.calc.genecp}',
    },
    'orca-out': {
        'calculator': 'ORCA',
        'primitive_data': {
            r'Total Charge\s+Charge\s+\.+\s+(\d+)' : {
                'important' : True,
                'selection' : -1,
                'key' : 'charge',
                'type' : int,
            },
            r'Multiplicity\s+Mult\s+\.+\s+(\d+)' : {
                'important' : True,
                'selection' : -1,
                'key' : 'multiplicity',
                'type' : int,
            },
            # r'Center *Atomic *Atomic *Coordinates.*\((.*)\).*\n': {
            #     'important' : True,
            #     'selection' : -1,
            #     'key' : 'unit',
            #     'type' : str,
            #     },
            r'CARTESIAN COORDINATES \(ANGSTROEM\)\n-*\n([\s\S]*?)\n\n-*' : {
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
                        'index' : ':,1:',
                    }
                    ],
                },
            r'Total Energy\s+:\s+.*Eh\s+(.*) eV' : {
                'important' :  True,
                'selection' : -1,
                'type' : float,
                'key' : 'calc_arrays/potential_energy',
                },
            r'Total Dipole Moment\s+:\s+(.*)\n': {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'calc_arrays/dipole_moment',
                        'type' : float,
                        'index' : '0,:',
                        'postprocess': lambda x: x.flatten()
                    },
                    ],
                },
            # r'Quadrupole moment.*\n\s*(.*\n.*)\n': {
            #     'important' : True,
            #     'selection' : -1,
            #     'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            #     'key' : [
            #         {
            #             'key' : 'calc_arrays/quadrupole_moment',
            #             'type' : float,
            #             'index' : ':,[1,3,5]',
            #         }
            #         ],
            #     },
            },
        'synthesized_data' : OrderedDict({
            }),
    },
}
