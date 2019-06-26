"""
format_string
"""

import re
from collections import OrderedDict
from io import StringIO

import numpy as np
import pandas as pd

import chemdata
import atomtools
from .. import ext_types
from .. import ext_methods


FORMAT_STRING = {
    'mol': {
        'ignorance' : ('#',),
        'primitive_data' : {
            r'^(.*)\n' : {
                'important' : True,
                'selection' : -1,
                'key' : 'title',
                'type' : str,
                },
            r'^.*\n(.*)\n' : {
                'important' : True,
                'selection' : -1,
                'key' : 'comments_Program',
                'type' : str,
                },
            r'^.*\n.*\n(.*)\n' : {
                'important' : True,
                'selection' : -1,
                'key' : 'comments',
                'type' : str,
                },
            r'^.*\n.*\n.*\n(.*)\n' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: np.array(data.split()),
                'key' : [
                    {
                        'key' : 'natoms',
                        'index' : '0',
                        'type' : int,
                    },
                    {
                        'key' : 'nbonds',
                        'index' : '1',
                        'type' : int,
                    },
                    # {
                    #     'key' : 'natoms',
                    #     'index' : '0',
                    #     'type' : int,
                    # },
                    # {
                    #     'key' : 'natoms',
                    #     'index' : '0',
                    #     'type' : int,
                    # },
                ],
                },
            r'^.*\n.*\n.*\n.*\n([\s\S]*?)\nM\s+END' : {
                'important' : True,
                'selection' : -1,
                'key' : 'mol_content',
                'type' : str,
                },
            },
        'synthesized_data' : OrderedDict({
            'atoms_data' : {
                'prerequisite' : ['mol_content'],
                'equation' : lambda arrays: ext_methods.datablock_to_numpy('\n'.join(arrays['mol_content'].split('\n')[:arrays['natoms']])),
                },
            'symbols' : {
                'prerequisite' : ['atoms_data'],
                'equation' : lambda arrays: arrays['atoms_data'][:,3],
                'process' : lambda data, arrays: data.tolist(),
                },
            'positions' : {
                'prerequisite' : ['mol_content'],
                'equation' : lambda arrays: arrays['atoms_data'][:,:3],
                'delete' : ['atoms_data', 'mol_content'],
                },
            }),
    },
}

