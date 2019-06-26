"""
format_string
"""
from collections import OrderedDict
from .. import ext_methods

FORMAT_STRING = {
    'xyz': {
        'primitive_data'  : OrderedDict({
            r'^\s*(\d+)\n.*\n[\s\S]*': {
                'important': True,
                'selection' : 0,
                'key' : 'natoms',
                'type' : int,
            },
            r'\d+\n(.*)\n[\s\S]*':{
                'important': True,
                'selection' : -1,
                'key' : 'comments',
                'type' : str,
            },
            r'\d+\n.*\n([\s\S]*)$':{
                'important': True,
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
                    {
                        'key' : 'velocities',
                        'type' : float,
                        'index' : ':,4:7',
                    },
                    # {
                    #     'key' : 'content_length',
                    #     'type' : float,
                    #     'process' : lambda data, arrays: data.shape[-1],
                    # },
                    ],
            },
            r'\d+\n.*\n([\s\S]*)':{
                'important': True,
                'selection' : 'all',
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(\
                    data)[:,1:4].reshape((-1, arrays['natoms'], 3)),
                'key' : [
                    {
                        'key' : 'all_positions',
                        'type' : float,
                        'index' : ':,1:4,:'
                    }
                ],
            },
        }),
        'synthesized_data' : OrderedDict({
        }),
        'writer_formats' : '{atoms.natoms}\n{atoms.GET_JSON()}\n{atoms.get_symbols_positions()}\n',
        'multiframe': True,
    },
}
