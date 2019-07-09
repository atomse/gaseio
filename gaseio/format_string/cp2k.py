"""
format_string
"""



import re
from collections import OrderedDict
import atomtools
import numpy as np




from .. import ext_types
from .. import ext_methods
from ..format_parser import read


def parse_cp2k_cell(arrays):
    _cell_data = arrays['_cell_data']
    ABC_PATTERN = r'ABC\s+(\d+.*?)\s+(\d+.*?)\s+(\d+.*?)\n'
    AlphaBetaGamma_PATTERN = r'ALPHA_BETA_GAMMA\s+(\d+.*?)\s+(\d+.*?)\s+(\d+.*?)\n'
    COMPLETE_CELL_PATTERN = r'(A\s+\d+[\s\S]*?\n\s*B\s+\d+[\s\S]*?\n\s*C\s+\d+[\s\S]*?)\n'
    if re.findall(ABC_PATTERN, _cell_data):
        a, b, c = re.findall(ABC_PATTERN, _cell_data)[0]
        if re.findall(AlphaBetaGamma_PATTERN, _cell_data):
            alpha, beta, gamma = re.findall(AlphaBetaGamma_PATTERN, _cell_data)[0]
        else:
            alpha, beta, gamma = 90., 90., 90.
        cell = atomtools.geo.cellpar_to_cell((float(a), float(b), float(c), float(alpha), float(beta), float(gamma)))
    elif re.findall(COMPLETE_CELL_PATTERN, _cell_data):
        cell = ext_methods.datablock_to_numpy(re.findall(COMPLETE_CELL_PATTERN, _cell_data)[0])[:,1:4]
    return cell


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
                ],
            },
            r'&CELL.*?\n([\s\S]*?\s*A[\sB][\s\S]*?)&END.*' : {
                'important' : True,
                'selection' : -1,
                'key' : '_cell_data'
            },
            r'CHARGE\s+(\d+)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'key' : 'charge',
                'type' : int,
            },
            r'CUTOFF\s+(\d+.*)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/cutoff',
                'type' : float,
            },
            r'MAX_FORCE\s+(\d+.*)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/max_force',
                'type' : float,
            },
        },
        'synthesized_data' : OrderedDict({
            'cell' : {
                'prerequisite' : ['_cell_data'],
                'equation' : lambda arrays: parse_cp2k_cell(arrays),
                'delete' : ['_cell_data'],
            },
        }),
    },
    'cp2k-out': {
        'calculator': 'CP2K',
        'primitive_data': {
            r'ATOMIC COORDINATES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n{2,}' : {
                # 'debug' : True,
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
                        'index' : ':,7',
                        'type' : float,
                    },
                    {
                        'key' : 'mass',
                        'index' : ':,8',
                        'type' : float,
                    },
                ],
            },
            re.compile(r'ATOMIC COORDINATES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n{2,}') : {
                # 'debug' : True,
                'important' : True,
                'selection' : 'all',
                # 'join' : '\n',
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'all_positions',
                        'index' : ':,4:7',
                        'type' : float,
                        'process' : lambda data, arrays: np.array(data).astype(float).reshape((-1, \
                                    len(arrays['positions']), 3))
                    },
                ],
            },
            r'ATOMIC FORCES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n.*SUM OF ATOMIC FORCES' : {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'forces',
                        'index' : ':,3:6',
                        # 'type' : float,
                        'process' : lambda data, arrays: np.array(data).astype(float)\
                                                         * atomtools.unit.trans_force('au')
                    },
                ],
            },
            re.compile(r'ATOMIC FORCES.*\n+\s+.*Atom\s+Kind\s+Element.*\n+([\s\S]*?)\n.*SUM OF ATOMIC FORCES') : {
                'important' : False,
                'selection' : 'all',
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'all_forces',
                        'index' : ':,3:6',
                        # 'type' : float,
                        'process' : lambda data, arrays: np.array(data).astype(float).reshape((-1, \
                                    len(arrays['forces']), 3)) * atomtools.unit.trans_force('au')
                    },
                ],
            },
            r'ENERGY\| Total FORCE_EVAL.*\s{2,}([+-]\d+.*)\n' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/potential_energy',
                # 'type' : float,
                'process' : lambda data, arrays: float(data) * atomtools.unit.trans_energy('au', 'eV'),
            },
            re.compile(r'ENERGY\| Total FORCE_EVAL.*\s{2,}([+-]\d+.*)\n') : {
                'important' : False,
                'selection' : 'all',
                'key' : 'calc_arrays/all_potential_energy',
                # 'type' : float,
                'process' : lambda data, arrays: float(data) * atomtools.unit.trans_energy('au', 'eV'),
            },
            r'GEOMETRY OPTIMIZATION COMPLETED' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/geo_opt_done',
                'process' : lambda data, arrays: True if data else False,
            },
            r' VIB\| {10,}NORMAL MODES.*\n.*([\s\S]*?)-{10,}' : {
                'important' : False,
                'selection' : -1,
                'key' : '_frequency_data',
            },
            r'GLOBAL\| Run type {5,}(.+)\n' : {
                'important' : False,
                'selection' : -1,
                'key' : 'calc_arrays/runtype',
                'process' : lambda data, arrays: data.lower(),
            }
            },
        'synthesized_data' : OrderedDict({
            'calc_arrays/frequency' : {
                'prerequisite' : ['_frequency_data'],
                'equation' : lambda arrays: arrays['_frequency_data'],
            }
            }),
    },
}
