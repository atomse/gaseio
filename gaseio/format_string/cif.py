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
            r'loop_\n(_atom_site_[\s\S]*_z\n[\s\S]*?)(?:\n\n|_loop|loop|$)':{
                'important': True,
                'selection' : -1,
                'key' : '_atom_site',
                'type' : str,
            },
            r'_symmetry_space_group_name_H-M\s+[\']?(.*?)[\']?' : {
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
            r'loop_\n((?:_symmetry|_space)[\s\S]*?)(?:\n\n|_loop|loop|$)' : {
                'important' : False,
                'selection' : -1,
                'type' : str,
                'key' : '_space_group_symop',
            },
        }),
        'synthesized_data' : OrderedDict({
            '_atom_site_labels' : {
                'prerequisite' : '_atom_site',
                'equation' : lambda arrays: re.findall(r'(?:\n|^)_atom_site.*(?:\n)', arrays['_atom_site']),
            }
            'symbols' : {
                'prerequisite' : '_atom_site',
                'equation' : lambda arrays: fetch_symbols(arrays['_atom_site']),
            },
            'positions' : {
                'prerequisite' : '_atom_site',
                'equation' : lambda arrays: fetch_positions(arrays['_atom_site']),
            },
        }),
    },
}
