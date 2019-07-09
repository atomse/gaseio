"""
format_string
"""
import re
from collections import OrderedDict
import numpy as np
import atomtools
from .. import ext_methods

def cif_construct_cell(arrays):
    cell_a = float(arrays['_cell_length_a'])
    cell_b = float(arrays['_cell_length_b'])
    cell_c = float(arrays['_cell_length_c'])
    alpha = float(arrays['_cell_angle_alpha'])
    beta = float(arrays['_cell_angle_beta'])
    gamma = float(arrays['_cell_angle_gamma'])
    cell = atomtools.geo.cellpar_to_cell((cell_a, cell_b, cell_c, alpha, beta, gamma))
    return cell

def cif_parse_symbols(arrays):
    return ext_methods.regularize_symbols(arrays['_atom_site_fract']['_atom_site_label'].values)


def cif_parse_positions(arrays):
    if '_atom_site_fract' in arrays:
        frac_positions = arrays['_atom_site_fract'].loc[:, \
                        ['_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z']].values
        positions = frac_positions.dot(arrays['cell'])
    elif '_atom_site_cartn' in arrays:
        positions = arrays['_atom_site_cartn'].loc[:, \
                    ['_atom_site_cartn_x', '_atom_site_cartn_y', '_atom_site_cartn_z']].values
    return positions



FORMAT_STRING = {
    'cif': {
        'primitive_data'  : OrderedDict({
            # r'_atom_site_occupancy':{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'comments',
            #     'type' : str,
            # },
            r'loop_\n(_atom_site_[\s\S]*fract_z\n[\s\S]*?[A-Z][\s\S]*?)(?:\n\n|_|loop|$)':{
                'important': False,
                'selection' : -1,
                'key' : '_atom_site_fract',
                'process' : lambda data, arrays: ext_methods.datablock_to_dataframe(\
                                                 re.sub('\n_', ' _', data), header=0)
            },
            r'loop_\n(_atom_site_[\s\S]*cartn_z\n[\s\S]*?[A-Z][\s\S]*?)(?:\n\n|_|loop|$)':{
                'important': False,
                'selection' : -1,
                'key' : '_atom_site_cartn',
                'process' : lambda data, arrays: ext_methods.datablock_to_dataframe(\
                                                 re.sub('\n_', ' _', data), header=0)
            },
            r'_symmetry_space_group_name_H-M\s+[\']?(.*?)[\']?\n' : {
                'important' : False,
                'selection' : -1,
                'type' : str,
                'key' : '_symmetry_space_group',
            },
            r'_symmetry_Int_Tables_number\s+[\']?(.*?)[\']?\n' : {
                'important' : False,
                'selection' : -1,
                'type' : int,
                'key' : '_symmetry_int_tables_number',
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
            'cell' : {
                'prerequisite' : ['_cell_length_a', '_cell_length_b', '_cell_length_c',
                                  '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma'],
                'equation' : lambda arrays: cif_construct_cell(arrays),
                'delete' : ['_cell_length_a', '_cell_length_b', '_cell_length_c',
                            '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma'],
            },
            'symbols' : {
                'prerequisite' : [('_atom_site_fract', '_atom_site_cartn')],
                'equation' : lambda arrays: cif_parse_symbols(arrays),
            },
            'positions' : {
                'prerequisite' : [('_atom_site_fract', '_atom_site_cartn'), 'cell'],
                'equation' : lambda arrays: cif_parse_positions(arrays),
                # 'delete' : ['_atom_site_fract', '_atom_site_cartn'],
            },
        }),
    },
}
