"""
format_string
"""
from collections import OrderedDict
import numpy as np
import re

from .. import ext_types
from .. import ext_methods




siesta_format_string = {
    'calculator' : 'SIESTA',
    'ignorance' : ('#', ),
    'primitive_data'  : {
        r'%block AtomicCoordinatesAndAtomicSpecies([\s\S]*?)\n%endblock AtomicCoordinatesAndAtomicSpecies':{
            'important': True,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            'key' : [
                {
                    'key' : 'species_nums',
                    # 'debug' : True,
                    'type' : int,
                    'index' : ':,3',
                    'process' : lambda data, arrays: data.flatten() - 1,
                },
                {
                    'key' : 'positions',
                    'type' : float,
                    'index' : ':,0:3',
                },
                ],
        },
        r'%block ChemicalSpeciesLabel([\s\S]*?)\n%endblock ChemicalSpeciesLabel':{
            'important': True,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            'key' : [
                {
                    'key' : 'species_syms',
                    # 'debug' : True,
                    'type' : str,
                    'index' : ':,2',
                    'process' : lambda data, arrays: np.array([_.split('_')[0]\
                                                     for _ in data.flatten().tolist()]),
                },
                ],
        },
        r'%block LatticeVectors([\s\S]*?)\n%endblock LatticeVectors':{
            'important': True,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            'key' : 'cell',
        },
    },
    'synthesized_data' : OrderedDict({
        'symbols' : {
            'prerequisite' : ['species_syms', 'species_nums'],
            'equation' : lambda arrays: arrays['species_syms'][arrays['species_nums']].tolist(),
        },
    }),
}

siesta_out_format_string = siesta_format_string
ext_methods.update(siesta_out_format_string, {
    'primitive_data'  : {
        r'siesta: Final energy.*([\s\S]*?)\n\n' : {
            'important': False,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_dict(re.sub(r'siesta:\s+', '', data)),
            'key' : 'energy_block',
        },
        r'siesta: Constrained forces.*([\s\S]*?)siesta: -{20,}' : {
            'important': False,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            'key' : [
                {
                    'key' : 'forces',
                    'type' : float,
                    'index' : ':,2:',
                },
                ],
        },
        r'siesta: Stress tensor.*([\s\S]*?)\n\n' : {
            'important': False,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            'key' : [
                {
                    'key' : 'stress',
                    'type' : float,
                    'index' : ':,1:',
                },
                ],
        },
        r'%block LatticeVectors([\s\S]*?)\n%endblock LatticeVectors':{
            'important': True,
            'selection' : -1,
            'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
            'key' : 'cell',
        },
    },
    'synthesized_data' : OrderedDict({
        'potential_energy' : {
            # 'debug' : True,
            'prerequisite' : ['energy_block', ],
            'equation' : lambda arrays: arrays['energy_block']['Total'],
        },
    }),
})




FORMAT_STRING = {
    'siesta' : siesta_format_string,
    'siesta-out' : siesta_out_format_string,
}
