"""
format_string
"""
from collections import OrderedDict
from .. import ext_types
from .. import ext_methods

FORMAT_STRING = {
    'orca': {
        'calculator': 'ORCA',
        'ignorance' : ('#',),
        'primitive_data': {
            r'^\s*(start)\s*.*\n\s*title\s*.*\n' :{
                'important': True,
                'selection' : -1,
                'key' : 'calc_arrays/starttype',
                'type' : str
                },
            r'^\s*start\s*(.*)\n\s*title\s*.*\n' :{
                'important': True,
                'selection' : -1,
                'key' : 'calc_arrays/name',
                'type' : str
                },
            r'^\s*start\s*.*\n\s*title\s*(.*)\n' :{
                'important': True,
                'selection' : -1,
                'key' : 'comments',
                'type' : str
                },
            r'geometry units\s*(.*)\n' :{
                'important': True,
                'selection' : -1,
                'key' : 'unit',
                'type' : str
                },
            r'geometry units\s*.*\n([\s\S]*?)\n\s*end\n' :{
                'important': True,
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
                        'index' : ':,1:',
                    }
                    ]
                },
            r'basis\s*\n([\s\S]*?)\n\s*end\n+\s*task\s*.*\n' :{
                'important': True,
                'selection' : -1,
                'key' : 'basis',
                'type' : str,
                },
            r'basis\s*\n[\s\S]*?\n\s*end\n+\s*task\s*(.*)\n' :{
                'important': True,
                'selection' : -1,
                'key' : 'task',
                'type' : str,
                },
            },
        'synthesized_data' : OrderedDict({
            }),
    },

    'orca-out': {
        'calculator': 'NWCHEM',
        'ignorance' : ('#',),
        'primitive_data': {
            # r'^\s*(start)\s*.*\n\s*title\s*.*\n' :{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'calc_arrays/starttype',
            #     'type' : str
            #     },
            # r'^\s*start\s*(.*)\n\s*title\s*.*\n' :{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'calc_arrays/name',
            #     'type' : str
            #     },
            # r'^\s*start\s*.*\n\s*title\s*(.*)\n' :{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'comments',
            #     'type' : str
            #     },
            # r'geometry units\s*(.*)\n' :{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'unit',
            #     'type' : str
            #     },
            r'Output coordinates in angstroms[\s\S]*?[- ]*\n[\s\S]*?\n\s+Atomic Mass' :{
                'important': True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'symbols',
                        'type' : str,
                        'index' : ':,1',
                    },
                    {
                        'key' : 'positions',
                        'type' : float,
                        'index' : ':,3:',
                    }
                    ]
                },
            # r'basis\s*\n([\s\S]*?)\n\s*end\n+\s*task\s*.*\n' :{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'basis',
            #     'type' : str,
            #     },
            # r'basis\s*\n[\s\S]*?\n\s*end\n+\s*task\s*(.*)\n' :{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'task',
            #     'type' : str,
            #     },
            },
        'synthesized_data' : OrderedDict({
            }),
    },


}
