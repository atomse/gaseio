"""
format_string
"""

import re
from collections import OrderedDict
from io import StringIO

import numpy as np
import pandas as pd

import chemdata
import atomtools
from atomtools import Status


from .. import ext_types
from .. import ext_methods


ENERGY_ORDER = [
                r"CCSD\(?T\)?",
                r"CCSD", 
                r"CBSQ", 
                r"QCISD\(?T\)?", 
                r"QCISD", 
                r"MP4\(?SDQ\)?", 
                r"MP4\(?DQ\)?", 
                r"MP4\(?D\)?", 
                r"MP3", 
                r"MP2", 
                r"HF",
                ]


def get_value_by_order(properties, order):
    if properties is None:
        return None
    for _ord in order:
        # if properties.get(_ord, None):
        #     return properties.get(_ord)
        for item, val in properties.items():
            if re.match(_ord+'.*', item):
                return val

def gaussian_extract_frequency(logline, arrays):
    """
    extract frequency data from gaussian log
    """

    item_pattern = r'\s+(.*?)\s+-- '
    def parse_freq_lines(origin_lines, startline, num_lines, 
                         index, num_items, natoms):
        """
        #           1              2              3
        #           A              A              A
        #  Frequencies --   -754.3221            31.3611           174.9690
        #  Red. masses --      1.1484             6.5519             6.8477
        #  Frc consts  --      0.3850             0.0038             0.1235
        #  IR Inten    --   1827.3164             2.1140             0.0189
        #   Atom  AN      X  Y  Z    X  Y      Z    X      Y      Z
        #      1  15     0.00   0.05   0.00 0.00   0.00  -0.01     0.10   0.04   0.00
        #      2   6     0.00  -0.02   0.00    -0.20  -0.01   0.15     0.21  -0.09  -0.06
        #      3   1     0.00   0.00   0.00    -0.33  -0.03   0.07     0.29   0.03   0.00
        #      4   1    -0.01  -0.02  -0.02    -0.20  -0.01   0.24     0.39  -0.18  -0.14
        """
        # import pdb; pdb.set_trace()
        item_dict = {
            'Frequencies' : 'frequency',
            'Red. masses' : 'reduced_mass',
            'Frc consts'  : 'force_constant',
            'IR Inten'    : 'IR_intensity',
            'raman'       : 'Raman_activity',
            'depolar(p)'  : 'Depolar_p',
            'depolar(u)'  : 'Depolar_u',
        }
        lines = origin_lines[startline: startline+num_lines]
        # if DEBUG: print('line:', lines)
        if index+1 > len(lines[0].split()):
            return None
        data = {}
        line_i = 1
        data['symmetry'] = lines[line_i].split()[index]
        line_i += 1
        for line in lines[line_i:num_items+line_i]:
            # print(line)
            item_name, rs = line.split('--')
            item_name = item_dict[item_name.strip()]
            rs = rs.strip().split()[index]
            rs = float(rs)
            data[item_name] = rs
        line_i += num_items+1
        vector = [[0.0, 0.0, 0.0]] *natoms
        for line in lines[line_i:]:
            try:
                atom_number = int(line[0:14].split()[0]) -1
            except:
                break
            i_vector = line.split()[2+3*index:2+3*index+3]
            i_vector = list(map(lambda x: float(x), i_vector))
            # if DEBUG: print(i_vector)
            # vector.append(i_vector)
            vector[atom_number] = i_vector
            # if DEBUG: print(atom_number, i_vector)
        data['vector'] = vector
        return data


    lines = logline.split('\n')
    natoms = len(arrays['positions'])
    
    items_name = set(re.findall(item_pattern, logline))
    # for line in lines:
    #     if re.match('--', line):
    #         items_name.append((line.split('--')[0]).strip())
    #     elif re.match('Atom', line):
    #         break
    num_line_each = 2 + len(items_name) + 1 + natoms

    N_freq_per_block = 3
    freq = []
    for i in range(natoms//N_freq_per_block+1):
        for j in range(N_freq_per_block):
            data = parse_freq_lines(lines, num_line_each*i,
                num_line_each, j, len(items_name), natoms)
            if data is None:
                break
            # if DEBUG: print(i, j, data)
            freq.append(data)
        if data is None:
            break
    return freq







def get_block_data(line, columns=None, index_col=False, header=None):
    csv = pd.read_csv(StringIO(line), sep='\s+', index_col=index_col, header=header)
    if columns is None:
        return np.array(csv)
    # data = np.array(csv)[:,columns]
    data = np.array(csv.ix[:,columns])
    #try:
    #  data[np.isnan(data)] = 0.
    #except:
    #  pass
    return data


def parse_diagonal_data(inp_line, ndim, max_width,
    has_top = True, sindex=1, type='lower'):
    lines = inp_line.split('\n')
    row_i = line_i = 0
    xndim = ndim
    if has_top:
        header_line = 1
    else:
        header_line = 0
    rsdata = np.zeros((ndim, ndim))
    # rsdata[:] = np.nan
    while row_i < ndim:
        line = '\n'.join(lines[line_i:line_i+xndim+header_line])
        line = re.sub('^', '^XX ', line)
        line = re.sub('D(?=\+|\-)', 'E', line)
        data = get_block_data(line, index_col=0, header=header_line-1)
        rsdata[row_i: ndim, row_i: min(row_i+max_width, ndim)] = data
        row_i += max_width
        row_i = min(row_i, ndim)
        line_i += xndim +header_line
        xndim -= max_width
    rsdata[np.isnan(rsdata)] = 0
    rsdata += np.triu(rsdata.T, 1)
    return rsdata



def gaussian_extract_second_derivative_matrix(logline, arrays):
    # import pdb; pdb.set_trace()
    # if re.match(r'\s+R\d\s+', logline):
    arrays['hessian_type'] = 'Internal'
    ndim = len(arrays['calc_arrays/internal_coords'])
    # else:
    #     arrays['hessian_type'] = 'Cartesian'
    #     natoms = len(arrays['positions'])
    #     ndim = 3*natoms
    return parse_diagonal_data(logline, ndim=ndim, max_width=5)

# def second_order_forces_consts(logline, fctype, ndim):
#     if fctype == 'cartesian':
#         if ' Force constants in Cartesian coordinates:' in logline:
#             return parse_diagonal_data(logline,
#                 ' Force constants in Cartesian coordinates: \n',
#                 '\n FormGI is forming the', ndim=ndim, max_width=5)
#     else:
#         if ' Force constants in internal coordinates:' in logline:
#             ndim = len(get_internal_coordinations(logline))
#             return parse_diagonal_data(logline,
#                 ' Force constants in internal coordinates: \n',
#                 '\n Leave Link  716 at', ndim=ndim, max_width=5)


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
            r'#\s*([\s\S]*?)\n\s*\n[\s\S]*?\n\s*\n' : {
                    'important': True,
                    'selection' : 0,
                    'type': str,
                    'key' : 'calc_arrays/command',
                    'process' : lambda data, arrays: data.replace('\n', ' ').strip(),
                },
            r'#\s*[\s\S]*?\n\s*\n([\s\S]*?)\n\s*\n' : {
                    'important' : True,
                    'selection' : 0,
                    'type' : str,
                    'key' : 'comments',
                    'process' : lambda data, arrays: data.replace('\n', ' ').strip(),
                },
            r'#\s*[\s\S]*?\n\s*\n[\s\S]*?\n\s*\n\s*([+-]?\d+)[, ]*\d+.*' : {
                    'important' : True,
                    'selection' : 0,
                    'type' : int,
                    'key' : 'charge'
                },
            r'#\s*[\s\S]*?\n\s*\n[\s\S]*?\n\s*\n\s*[+-]?\d+[, ]*(\d+).*' : {
                    'important' : True,
                    'selection' : 0, 
                    'type' : int,
                    'key' : 'multiplicity'
                },
            r'\n\s*[+-]?\d+[, ]*\d+.*\s*\n([\s\S]*?)\n\s*\n' : {
                    # 'debug' : True,
                    'important' : True,
                    'selection' : 0, 
                    'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                    'key' : 'gaussian_coord_datablock',
                    # 'key' : [
                    #     {
                    #         'key' : 'symbols',
                    #         'type' : str,
                    #         'index' : ':,0',
                    #         'process' : lambda data, arrays: ext_types.ExtList(data.tolist()),
                    #     },
                    #     {
                    #         'key' : 'positions',
                    #         'type' : float,
                    #         'index' : ':,1:4',
                    #     },
                    #     {
                    #         'key' : 'tags',
                    #         'type' : str,
                    #         'index' : ':,4',
                    #     },
                    # ],
                },
            r'\n\s*[+-]?\d+[, ]*\d+.*\s*\n[\s\S]*?\n\s*\n([\s\S]*)' : {
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
            'symbols' : {
                'prerequisite' : ['gaussian_coord_datablock'],
                'equation' : lambda arrays: arrays['gaussian_coord_datablock'][:,0],
                },
            'constraint' : {
                'prerequisite' : ['gaussian_coord_datablock'],
                'condition' : lambda arrays: arrays['gaussian_coord_datablock'].shape[1] >= 5 and \
                                             np.logical_or(arrays['gaussian_coord_datablock'][:,1]==0, arrays['gaussian_coord_datablock'][:,1]==-1).all(),
                'equation' : lambda arrays: arrays['gaussian_coord_datablock'][:,1] == -1,
                },
            'positions' : {
                'prerequisite' : ['gaussian_coord_datablock'],
                'equation' : lambda arrays: arrays['gaussian_coord_datablock'][:,2:5] if 'constraint' in arrays else arrays['gaussian_coord_datablock'][:,1:4],
                },
            'tags' : {
                'prerequisite' : ['gaussian_coord_datablock'],
                'condition' : lambda arrays: arrays['gaussian_coord_datablock'].shape[1] >= 6 if 'constraint' in arrays else \
                                             arrays['gaussian_coord_datablock'].shape[1] >= 5,
                'equation' : lambda arrays: arrays['gaussian_coord_datablock'][:,5] if 'constraint' in arrays else \
                                            arrays['gaussian_coord_datablock'][:,4],
                'delete' : ['gaussian_coord_datablock'],
                },
            }),
        # 'writer_formats': '%nproc={atoms.maxcore}\n%mem={atoms.maxmem}B\n%chk={randString()}.chk\n#p force b3lyp/6-31g(d)\n\ngase\n\n{atoms.charge} {atoms.multiplicity}\n{atoms.get_symbols_positions()}{atoms.calc.connectivity}{atoms.calc.genecp}',
    },
    'gaussian-out': {
        'calculator': 'Gaussian',
        'primitive_data': {
            r'Charge\s+=\s+(-?\d+)' : {
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
            # r'Center *Atomic *Atomic *Coordinates.*\((.*)\).*\n': {
            #     'important' : True,
            #     'selection' : -1,
            #     'key' : 'unit',
            #     'type' : str,
            #     },
            r'\n (1[\\|\|]1[\\|\|][\s\S]*?[\\|\|]\s*[\\|\|])\s*@\n': {
                # 'debug' : True,
                # 'important' : True,
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
            r'\n Dipole moment.*\n\s*(X=\s+.*)\n': {
                'important' : False,
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
            r'\n Quadrupole moment.*\n\s*(XX=\s+.*\n.*)\n': {
                'important' : False,
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
            r'Center\s+Atomic\s+Forces\(Hartrees/Bohr\)\n\s+Number\s+Number\s+X\s+Y\s+Z\n ---*\n([\s\S]*?)---*' : {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'calc_arrays/forces',
                        'type' : float,
                        'index' : ':,2:',
                    },
                    ],
                },
            r'and normal coordinates:\n([\s\S]*?)\n ---[\s\S]*?Thermochemistry' : {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: gaussian_extract_frequency(data, arrays),
                'key' : 'frequency',
                },
            r'Initial Parameters[\s\S]*?Name.*Value.*\n\s-*\n([\s\S]*?)\n\s----*': {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy(data),
                'key' : [
                    {
                        'key' : 'calc_arrays/internal_coords',
                        'type' : str,
                        'index' : ':,1',
                    },
                    # {
                    #     'key' : 'calc_arrays/internal_coords_definition',
                    #     'type' : str,
                    #     'index' : ':,2',
                    # },
                    # {
                    #     'key' : 'calc_arrays/internal_coords_value',
                    #     'type' : float,
                    #     'index' : ':,3',
                    # },
                    ]
                },
            r' The second derivative matrix:\n([\s\S]*?)\n ITU' : {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: gaussian_extract_second_derivative_matrix(data, arrays),
                'key' : 'Hessian',
                },
            r'Normal termination' : {
                'important' : False,
                'selection' : 'all',
                'key' : 'normal_termination',
                },
            r'Error termination' : {
                'important' : False,
                'selection' : 'all',
                'key' : 'error_termination',
                },
            r'SCF Done:  E\(.*?\)\s=\s*([+-]?\d+\.\d+E?[+-]?[0-9]*)\s+' : {
                'important' : False,
                'selection' : -1,
                'key' : 'possible_potential_energy',
                'type' : float,
                },
            },
        'synthesized_data' : OrderedDict({
            'calc_arrays/status' : {
                'equation' : lambda arrays: Status.error if 'error_termination' in arrays else \
                                            Status.complete if 'normal_termination' in arrays else \
                                            Status.running if atomtools.file.file_active(arrays['absfilename']) else\
                                            Status.stopped,
                'deletion' : ['error_termination', 'normal_termination'],
                },
            'symbols' : {
                'prerequisite' : ['numbers'],
                'equation' : lambda arrays: np.array([chemdata.get_element(_) for _ in arrays['numbers']]),
                'process' : lambda data, arrays: ext_types.ExtList(data.tolist()),
            },
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
                'equation' : lambda arrays: re.match(r'\s*#\s*(.*?)$', arrays['gaussian_datablock'][1])[1],
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
            'calc_arrays/potential_energy' : {
                'prerequisite' : ['possible_potential_energy'],
                'equation' : lambda arrays: float(get_value_by_order(arrays.get('calc_arrays/results', None), 
                                                  ENERGY_ORDER) or arrays['possible_potential_energy'])\
                                            * atomtools.unit.trans_energy('au', 'eV'),
                'delete' : ['possible_potential_energy'],
                },
            'calc_arrays/zero_point_energy' : {
                'prerequisite' : ['calc_arrays/results/ZeroPoint'],
                'equation' : lambda arrays: float(arrays['calc_arrays/results/ZeroPoint']) *\
                                            atomtools.unit.trans_energy('au', 'eV'),
                },
            }),
    },
}

