"""
format_string
"""

import re
from collections import OrderedDict

import numpy as np
import pandas as pd

from .. import ext_types
from .. import ext_methods


def parse_pubchem_json_atoms(data):
    """
    parse json formated atoms in pubchem system
    """
    res = dict()
    atoms = data['atoms']
    res_id = data['id']['id']['cid']
    res['numbers'] = atoms['element']
    coords = data['coords'][0]
    conformers = coords['conformers']
    # print(conformers)
    conform = conformers[0]
    x, y, z, conform_data = conform['x'], conform['y'], conform['z'], conform['data']
    res['positions'] = np.vstack([x, y, z]).T
    natoms = len(res['numbers'])
    bonds = data['bonds']
    bond1 = bonds['aid1']
    bond2 = bonds['aid2']
    bond_orders = bonds['order']
    connectivity = np.zeros((natoms, natoms))
    for a1, a2, order in zip(bond1, bond2, bond_orders):
        a1 -= 1
        a2 -= 1
        connectivity[a1][a2] = connectivity[a2][a2] = order
    res['connectivity'] = connectivity
    res['pubchem'] = {
        'data': coords['data'],
        'conform_data': conform_data,
        'props': data['props'],
        'count': data['count'],
        'id': res_id,
    }
    return res


def parse_pubchem_json(data, index=':'):
    """
    parse a given pubchem-json and give out gase json
    """
    import json
    json_data = data
    if isinstance(data, str):
        json_data = json.loads(data)
    assert isinstance(json_data, dict), f'data is {type(data)}, should be str/dict'
    if 'PC_Compounds' in json_data:
        json_data = json_data['PC_Compounds']
    elif '_record' in json_data:
        json_data = json_data['_record']
    if index and isinstance(json_data, list):
        if isinstance(json_data, int) or isinstance(index, str) and index.isdigit():
            index = int(index)
            if index >= len(json_data):
                index = len(json_data) - 1
        json_data = eval(f'json_data[{index}]')
    if isinstance(json_data, dict):
        json_data = [json_data]
    results = []
    for js_atoms in json_data:
        results.append(parse_pubchem_json_atoms(js_atoms))
    if isinstance(index, int):
        results = results[0]
    return results


def try_convert(s):
    if re.match(r'^[+-]?\d+$', s):
        return int(s)
    elif re.match(r'^[+-]?\d*\.\d+$', s) or re.match(r'^[+-]?\d+\.\d*$', s):
        return float(s)
    return s


def parse_sdf_props(data):
    items = data.split("> <")
    res = dict()
    for _item in items:
        split_pos = _item.find('>')
        key, val = _item[:split_pos].strip(), _item[split_pos+1:].strip()
        if '\n' in val:
            val = val.split('\n')
            for i, line in enumerate(val):
                if len(line.split()) > 1:
                    line = line.split()
                    line = [try_convert(x) for x in line]
                else:
                    line = try_convert(line)
                val[i] = line
        else:
            val = try_convert(val)
        key = key.lower()
        res[key] = val
    return res


FORMAT_STRING = {
    'pubchem-json': {
        'parser_type': 'customized',
        'parser': parse_pubchem_json,
    },
    'sdf': {
        'ignorance': ('#',),
        # 'ignorance' : r'\s*#.*\n',
        'primitive_data': {
            r'^(.*)\n': {
                'important': True,
                'selection': -1,
                'key': 'title',
                'type': str,
            },
            r'^.*\n +(.*)\n': {
                'important': True,
                'selection': -1,
                'key': 'software',
                'type': str,
            },
            r'^.*\n.*\n(.*)\n': {
                'important': True,
                'selection': -1,
                'key': 'comments',
                'type': str,
            },
            r'^.*\n.*\n.*\n(.*)\n': {
                'important': True,
                'selection': -1,
                'process': lambda data, arrays: np.array(data.split()),
                'key': [
                    {
                        'key': 'natoms',
                        'index': '0',
                        'type': int,
                    },
                    {
                        'key': 'nbonds',
                        'index': '1',
                        'type': int,
                    },
                    # {
                    #     'key' : 'natoms',
                    #     'index' : '0',
                    #     'type' : int,
                    # },
                    # {
                    #     'key' : 'natoms',
                    #     'index' : '0',
                    #     'type' : int,
                    # },
                ],
            },
            r'^.*\n.*\n.*\n.*\n([\s\S]*?)\nM\s+END': {
                'important': True,
                'selection': -1,
                'key': 'mol_content',
                'type': str,
            },
            r'> <([\s\S]+)\$\$\$\$': {
                'important': False,
                'selection': -1,
                'key': '_props',
                'type': str,
            },
        },
        'synthesized_data': OrderedDict({
            'atoms_data': {
                'prerequisite': ['mol_content'],
                'equation': lambda arrays: ext_methods.datablock_to_numpy('\n'.join(arrays['mol_content'].split('\n')[:arrays['natoms']])),
            },
            'symbols': {
                'prerequisite': ['atoms_data'],
                'equation': lambda arrays: arrays['atoms_data'][:, 3],
                'process': lambda data, arrays: data.tolist(),
            },
            'positions': {
                'prerequisite': ['mol_content'],
                'equation': lambda arrays: arrays['atoms_data'][:, :3].astype(float),
                'delete': ['atoms_data', 'mol_content'],
            },
            'props': {
                'prerequisite': ['_props'],
                'equation': lambda arrays: parse_sdf_props(arrays['_props']),
                'delete': ['_props'],
            },
        }),
    },
}
