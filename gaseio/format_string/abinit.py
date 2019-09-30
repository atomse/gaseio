"""
ABINIT Input/Output file parser



https://www.abinit.org/sites/default/files/infos/7.2/input_variables/varbas.html#rprim



"""


import os
import numpy as np
from collections import OrderedDict

from .. import ext_types
from .. import ext_methods

FORMAT_STRING = {
    'abinit': {
        'calculator': 'ABINIT',
        # 'ignorance' : r'\s*#.*\n',
        'ignorance': ('#',),
        'primitive_data': {
            r'natom\s+(\d+)\s*\n': {
                'important': True,
                'selection': -1,
                'type': int,
                'key': 'natoms',
            },
            r'\n\s*typat\s+(\d+.*)\s*\n': {
                'important': True,
                'selection': -1,
                'type': int,
                'key': '_typat',
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data)
            },
            r'\n\s*znucl\s+(\d+.*)\s*\n': {
                'important': True,
                'selection': -1,
                'type': int,
                'key': '_znucl',
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data).reshape((-1,))
            },
            r'\n\s*xred\s*([\s\S]*?)(?:\n{2,}|\n$|$|[^\d\.\s])': {
                # 'debug' : True,
                'important': True,
                'selection': -1,
                'type': float,
                'key': '_xred',
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data)
            },
            r'\n\s*rprim\s*([\s\S]*?)(?:\n{2,}|\n$|$|[^\d\.\s])': {
                # 'debug' : True,
                'important': True,
                'selection': -1,
                'type': float,
                'key': 'cell',
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data)
            },
        },
        'synthesized_data': OrderedDict({
            'numbers': {
                # 'debug' : True,
                'prerequisite': ['_znucl', '_typat'],
                'equation': lambda arrays: arrays['_znucl'][arrays['_typat']-1].reshape((-1, )),
            },
            'positions': {
                'prerequisite': ['_xred'],
                'equation': lambda arrays: arrays['_xred'].dot(arrays['cell']),
            }
        }),
    },
    'abinit-out': {
        'calculator': 'ABINIT',
        'primitive_data': {
            r'Total Charge\s+Charge\s+\.+\s+(\d+)': {
                'important': True,
                'selection': -1,
                'key': 'charge',
                'type': int,
            },
            r'Multiplicity\s+Mult\s+\.+\s+(\d+)': {
                'important': True,
                'selection': -1,
                'key': 'multiplicity',
                'type': int,
            },
            # r'Center *Atomic *Atomic *Coordinates.*\((.*)\).*\n': {
            #     'important' : True,
            #     'selection' : -1,
            #     'key' : 'unit',
            #     'type' : str,
            #     },
            r'CARTESIAN COORDINATES \(ANGSTROEM\)\n-*\n([\s\S]*?)\n\n-*': {
                'important': True,
                'selection': -1,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'symbols',
                        'type': str,
                        'index': ':,0',
                        'process': lambda data, arrays: data.tolist(),
                    },
                    {
                        'key': 'positions',
                        'type': float,
                        'index': ':,1:',
                    }
                ],
            },
            r'Total Energy\s+:\s+.*Eh\s+(.*) eV': {
                'important':  True,
                'selection': -1,
                'type': float,
                'key': 'calc_arrays/potential_energy',
            },
            r'Total Dipole Moment\s+:\s+(.*)\n': {
                'important': True,
                'selection': -1,
                'process': lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key': [
                    {
                        'key': 'calc_arrays/dipole_moment',
                        'type': float,
                        'index': '0,:',
                        'postprocess': lambda x: x.flatten()
                    },
                ],
            },
        },
        'synthesized_data': OrderedDict({
        }),
    },
}
