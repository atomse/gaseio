"""
format_string
"""

import re
from collections import OrderedDict

import atomtools
from .. import ext_types
from .. import ext_methods


ENERGY_ORDER = ["CCSD(T)", "CCSD", "MP4SDQ", "MP4DQ", "MP4D", "MP3", "MP2", "HF"]


def get_item_energy(properties, order=ENERGY_ORDER):
    for _ord in order:
        if properties.get(_ord, None):
            return properties.get(_ord)

FORMAT_STRING = {
    'gaussian': {
        'calculator': 'Gaussian',
        'primitive_data' : {
            r'%npro.*=(\d+)\s*\n' : {
                    'important': False,
                    'selection' : -1,
                    'type': int,
                    'key' : 'maxcore',
                },
            r'%mem.*=(\d+.*)\s*\n' : {
                    'important': False,
                    'selection' : -1,
                    'type': str,
                    'key' : 'maxmem',
                },
            r'#\s*([\s\S]*?)\n\n.*\n\n.*-?\d+\s*\d+\s*\n' : {
                    'important': True,
                    'selection' : -1,
                    'type': str,
                    'key' : 'calc_arrays/command',
                },
            r'#\s*[\s\S]*?\n\n(.*)\n\n.*-?\d+\s*\d+\s*\n' : {
                    'important' : True,
                    'selection' : -1,
                    'type' : str,
                    'key' : 'comments',
                },
            r'#\s*[\s\S]*?\n\n.*\n\n.*(-?\d+)\s*\d+\s*\n' : {
                    'important' : True,
                    'selection' : -1,
                    'type' : int,
                    'key' : 'charge'
                },
            r'#\s*[\s\S]*?\n\n.*\n\n.*-?\d+\s*(\d+)\s*\n' : {
                    'important' : True,
                    'selection' : -1,
                    'type' : int,
                    'key' : 'multiplicity'
                },
            r'\n\n.*-?\d+\s*\d+\s*\n([\s\S]*?)\n\n' : {
                    'important' : True,
                    'selection' : -1,
                    'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                    'key' : [
                        {
                            'key' : 'symbols',
                            'type' : str,
                            'index' : ':,0',
                        },
                        {
                            'key' : 'positions',
                            'type' : float,
                            'index' : ':,1:4',
                        },
                    ],
                },
            r'#\s*[\s\S]*?\n\n.*\n\n.*-?\d+\s*\d+\s*\n[\s\S]*?\n\n([\s\S])' : {
                    'important' : True,
                    'selection' : -1,
                    'type' : str,
                    'key' : 'calc_arrays/appendix'
                },
            r'#[\s\S]*?connectivity[\s\S]*?\n\n[\s\S]*?\n\s*\n\s*([\d\n\. ]*)\n\n':{
                    'important': False,
                    'selection' : -1,
                    'type' : str,
                    'key' : 'calc_arrays/connectivity',
                },
            r'#[\s\S]*?gen[\s\S]*?\n\n[\s\S]*?\n\s*\n\s*[\d\n\. ]*\n\n([A-Z][a-z]?[\s\S]*?\n\n[A-Z][a-z]?.*\d\n[\s\S]*?)\n\n':{
                    'important': False,
                    'selection' : -1,
                    'type' : str,
                    'key' : 'calc_arrays/genecp',
                },
            r'(\$NBO.*\$END)':{
                    'important': False,
                    'selection' : -1,
                    'type' : str,
                    'key' : 'calc_arrays/nbo',
                },
            },
        'synthesized_data' : OrderedDict({
            }),
        # 'writer_formats': '%nproc={atoms.maxcore}\n%mem={atoms.maxmem}B\n%chk={randString()}.chk\n#p force b3lyp/6-31g(d)\n\ngase\n\n{atoms.charge} {atoms.multiplicity}\n{atoms.get_symbols_positions()}{atoms.calc.connectivity}{atoms.calc.genecp}',
    },
    'gaussian-out': {
        'calculator': 'Gaussian',
        'primitive_data': {
            r'Charge\s+=\s+(-*\d+)' : {
                'important' : True,
                'selection' : -1,
                'key' : 'charge',
                'type' : int,
            },
            r'Multiplicity\s+=\s+(\d+)' : {
                'important' : True,
                'selection' : -1,
                'key' : 'multiplicity',
                'type' : int,
            },
            r'Center *Atomic *Atomic *Coordinates.*\((.*)\).*\n': {
                'important' : True,
                'selection' : -1,
                'key' : 'unit',
                'type' : str,
                },
            r'\n (1[\\|\|]1[\\|\|][\s\S]*?[\\|\|][\\|\|])@\n': {
                # 'debug' : True,
                'important' : True,
                'selection' : -1,
                'key' : 'gaussian_datastring',
                'type' : str,
                'process' : lambda data, arrays: data.replace('\n ', '').replace('\\', '|').strip()
                },
            r'Center.* Atomic *Atomic *Coordinates.*\(.*\).*\n.*\n\s*-*\s*\n([\s\S]*?)\n\s*-+\s*\n' : {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'numbers',
                        'type' : int,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'positions',
                        'type' : float,
                        'index' : ':,3:',
                    }
                    ],
                },
            r'Dipole moment.*\n\s*(.*)\n': {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'calc_arrays/dipole_moment',
                        'type' : float,
                        'index' : '[0],[1,3,5]',
                        'postprocess': lambda x: x.flatten()
                    },
                    ],
                },
            r'Quadrupole moment.*\n\s*(.*\n.*)\n': {
                'important' : True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'calc_arrays/quadrupole_moment',
                        'type' : float,
                        'index' : ':,[1,3,5]',
                    }
                    ],
                },
            },
        'synthesized_data' : OrderedDict({
            'gaussian_datablock' : {
                'prerequisite' : ['gaussian_datastring'],
                'equation' : lambda arrays: arrays['gaussian_datastring'].split('||'),
            },
            'calc_arrays/config' : {
                'prerequisite' : ['gaussian_datablock'],
                'equation' : lambda arrays: arrays['gaussian_datablock'][0],
                },
            'calc_arrays/command' : {
                'prerequisite' : ['gaussian_datablock'],
                'equation' : lambda arrays: arrays['gaussian_datablock'][1],
                },
            'comments' : {
                'prerequisite' : ['gaussian_datablock'],
                'equation' : lambda arrays: arrays['gaussian_datablock'][2],
                },
            'calc_arrays/geometry' : {
                'prerequisite' : ['gaussian_datablock'],
                'equation' : lambda arrays: arrays['gaussian_datablock'][3],
                },
            'calc_arrays/results' : {
                'prerequisite' : ['gaussian_datastring'],
                'equation' : lambda arrays: ext_methods.string_to_dict(re.findall(r'\|\|(Version=.*?)\|\|', 
                                            arrays['gaussian_datastring'])[-1]),
                },
            'potential_energy' : {
                'prerequisite' : ['calc_arrays/results'],
                'equation' : lambda arrays: float(get_item_energy(arrays['calc_arrays/results'],
                                            ENERGY_ORDER)) * atomtools.unit.trans_energy('au', 'eV'),
                },
            }),
    },
}

