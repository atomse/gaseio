"""
format_string
"""
from collections import OrderedDict
from .. import ext_methods

FORMAT_STRING = {
    'cif': {
        'primitive_data'  : OrderedDict({
            r'_atom_site_occupancy':{
                'important': True,
                'selection' : -1,
                'key' : 'comments',
                'type' : str,
            },
            r'_atom_site_occupancy\n([\s\S]*?)[_\n$]':{
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
                        'key' : 'primitive_positions',
                        'type' : float,
                        'index' : ':,1:4',
                    },
                    {
                        'key' : 'occupancy',
                        'type' : float,
                        'index' : ':,4',
                        'process' : lambda data, arrays: data.tolist(),
                    },
                ],
            },
            r'_symmetry_space_group_name_H-M\s+\'(.*?)\'' : {
                'important' : False,
                'selection' : -1,
                'type' : str,
                'key' : 'symmetry_space_group',
            },
            r'_cell_angle_alpha\s+(.*?)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : float,
                'key' : '_cell_angle_alpha'
            },
            r'_cell_angle_beta\s+(.*?)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : float,
                'key' : '_cell_angle_beta'
            },
            r'_cell_angle_gamma\s+(.*?)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : float,
                'key' : '_cell_angle_gamma'
            },
            r'_cell_length_a\s+(.*?)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : float,
                'key' : '_cell_length_a'
            },
            r'_cell_length_b\s+(.*?)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : float,
                'key' : '_cell_length_b'
            },
            r'_cell_length_c\s+(.*?)\s*\n' : {
                'important' : False,
                'selection' : -1,
                'type' : float,
                'key' : '_cell_length_c'
            },
        }),
        'synthesized_data' : OrderedDict({
        }),
    },
}
