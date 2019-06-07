"""
format_string
"""
from collections import OrderedDict
from .. import ext_types
from .. import ext_methods

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
        # 'writer_formats': '%nproc={atoms.maxcore}\n%mem={atoms.maxmem}B\n%chk={randString()}.chk\n#p force b3lyp/6-31g(d)\n\natomse\n\n{atoms.charge} {atoms.multiplicity}\n{atoms.get_symbols_positions()}{atoms.calc.connectivity}{atoms.calc.genecp}',
    },
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
                    'type' :ext_types.ExtDict,
                    'key' : 'calc_arrays/geometry',
                },
            r'SCF\s*\n([\s\S]*?)[eE][nN][dD]' : {
                    'important': True,
                    'selection' : -1,
                    'type' :ext_types.ExtDict,
                    'key' : 'calc_arrays/scf',
                },
            r'XC\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': True,
                'selection' : -1,
                'type' :ext_types.ExtDict,
                'key' : 'calc_arrays/xc',
                },
            r'BASIS\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': True,
                'selection' : -1,
                'type' :ext_types.ExtDict,
                'key' : 'calc_arrays/basis',
                },
            r'BECKEGRID\s*\n([\s\S]*?)[eE][nN][dD]' : {
                'important': False,
                'selection' : -1,
                'type' :ext_types.ExtDict,
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
                'type' :ext_types.ExtDict,
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
    'xyz': {
        'primitive_data'  : {
            r'(\d+)\n(.*)\n([\s\S]*)':{
                'groups': [('natoms', int), ('comments', str),
                      (('symbols', str, ':arrays[\'natoms\'],0'),
                        ('positions', float, ':arrays[\'natoms\'],1:'),
                        ('velocities', float, ':arrays[\'natoms\'],4:'))],
                'important': True,
                },
        },
        'writer_formats' : '{atoms.natoms}\n{atoms.GET_JSON()}\n{atoms.get_symbols_positions()}\n',
        'multiframe': True,
    },
    'nwchem': {
        'calculator': 'NWCHEM',
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
            r'Center.* Atomic *Atomic *Coordinates.*\(.*\).*\n.*\n\s*-*\s*\n([\s\S]*?)\n\s*-+\s*\n': {
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
            }),
    },
}
