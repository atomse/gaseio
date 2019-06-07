"""
format_string
"""
from collections import OrderedDict
from .. import ext_types
from .. import ext_methods

FORMAT_STRING = {
    'adf' : {
        'calculator': 'ADF',
        'ignorance': ('!',),
        'primitive_data'  : {
            r'ATOMS cartesian\s*\n([\s\S]*?)[eE][nN][dD]':{
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
            r'CHARGE\s+(-?\d+)' : {
                    'important' : True,
                    'selection' : -1,
                    'type' : int,
                    'key' : 'charge'
                },
            r'GEOMETRY\s*\n([\s\S]*?)[eE][nN][dD]' : {
                    'important': False,
                    'selection' : -1,
                    # 'type' :ext_types.ExtDict,
                    'key' : 'calc_arrays/geometry',
                },
            r'SCF\s*\n([\s\S]*?)[eE][nN][dD]' : {
                    'important': True,
                    'selection' : -1,
                    # 'type' :ext_types.ExtDict,
                    'key' : 'calc_arrays/scf',
                },
            r'XC\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': True,
                'selection' : -1,
                # 'type' :ext_types.ExtDict,
                'key' : 'calc_arrays/xc',
                },
            r'BASIS\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': True,
                'selection' : -1,
                # 'type' :ext_types.ExtDict,
                'key' : 'calc_arrays/basis',
                },
            r'BECKEGRID\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': False,
                'selection' : -1,
                # 'type' :ext_types.ExtDict,
                'key' : 'calc_arrays/beckegrid',
                },
            r'RELATIVISTIC\s*([\s\S]*?)\s*\n' : {
                'important': False,
                'selection' : -1,
                'type' :str,
                'key' : 'calc_arrays/relativistic',
                },
            r'AnalyticalFreq\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': False,
                'selection' : -1,
                # 'type' :ext_types.ExtDict,
                'key' : 'calc_arrays/freq',
                },
            r'TITLE\s*([\s\S]*?)\s*\n' : {
                'important': False,
                'selection' : -1,
                'type' :str,
                'key' : 'comments',
                },
            },
        'synthesized_data' : OrderedDict({
            }),
    },
}
