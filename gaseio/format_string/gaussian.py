"""
format_string
"""

import re
from collections import OrderedDict

import atomtools
from .. import ext_types
from .. import ext_methods


ENERGY_ORDER = ["CCSD(T)", "CCSD", "MP4SDQ", "MP4DQ", "MP4D", "MP3", "MP2", "HF"]


def get_value_by_order(properties, order):
    for _ord in order:
        if properties.get(_ord, None):
            return properties.get(_ord)

def gaussian_extract_frequency(logline, arrays):
    """
    extract frequency data from gaussian log
    """

    def parse_freq_lines(origin_lines, si, num_lines, index, num_items, natoms):
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
        item_dict = {
            'Frequencies' : 'Frequencies'
        }
        lines = origin_lines[si: si+num_lines]
        # if DEBUG: print('line:', lines)
        if index+1 > len(lines[0].split()):
            return None
        data = {}
        line_i = 1
        data['symmetry'] = lines[line_i].split()[index]
        line_i += 1
        for line in lines[line_i:num_items+line_i]:
            item_name = line.split('--')[0].strip().lower()
            if re.match('freq', item_name):
                item_name = 'freq'
            elif re.match('mass', item_name):
                item_name = 'reduced_mass'
            elif re.match('frc', item_name):
                item_name = 'frc_consts'
            elif re.match('ir', item_name):
                item_name = 'IR_intensities'
            elif re.match('raman', item_name):
                item_name = 'Raman_activity'
            elif re.match('dep', item_name):
                if re.match('(p)', item_name):
                    item_name = 'depolar_p'
                elif re.match('(u)', item_name):
                    item_name = 'depolar_u'
            # print(line)
            rs = line.split('--')[1]
            rs = rs.split()[index]
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
            if DEBUG: print(i_vector)
            # vector.append(i_vector)
            vector[atom_number] = i_vector
            if DEBUG: print(atom_number, i_vector)
        data['vector'] = vector
        return data


    lines = logline.split('\n')
    natoms = arrays['natoms']
    
    for line in lines:
        if re.match('--', line):
            item_name.append((line.split('--')[0]).strip())
        elif re.match('Atom', line):
            break
    num_line_each = 2 + len(item_name) + 1 + natoms

    for i in range(natoms):
        for j in range(3):
            data = parse_freq_lines(lines, start_i+num_line_each*i,
                num_line_each, j, len(item_name), natoms)
            if data is None:
                break
            # if DEBUG: print(i, j, data)
            freq.append(data)
        if data is None:
            break
    return freq





def get_gaussian_freuencies(logline, natoms):
    key_string = ' and normal coordinates:'
    # 'Harmonic frequencies (cm**-1), IR intensities (KM/Mole)'
    found = False
    head  = False
    counter = 0
    line_count = 3
    num_items = 0
    item_name = []
    freq = []
    lines = logline.split('\n')
    for (start_i, line) in zip(range(len(lines)), lines):
        if re.match(key_string, line):
            found = True
            break
    start_i += 1
    # if DEBUG: print(start_i, lines[start_i])
    for line in lines[start_i:]:
        if re.match('--', line):
            item_name.append((line.split('--')[0]).strip())
        elif re.match('Atom', line):
            break
    num_line_each = 2 + len(item_name) + 1 + natoms
    # if DEBUG: print(item_name, num_line_each)
    # print(si, ei)
    if lines[start_i:] == []:
        return None
    for i in range(natoms):
        for j in range(3):
            data = parse_freq_lines(lines, start_i+num_line_each*i,
                num_line_each, j, len(item_name), natoms)
            if data is None:
                break
            # if DEBUG: print(i, j, data)
            freq.append(data)
        if data is None:
            break
    return freq





def gaussian_extract_hessian(data):
    # head
    head_startswith = '                          '
    head0 = head1 = None
    for i, line in enumerate(data.split('\n')):
        if line.startswith(head_startswith):
            if not head0:
                head0 = i
            else:
                head1 = i
                break
    column_length = head1 - head0 - 1

    return data



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
        # 'writer_formats': '%nproc={atoms.maxcore}\n%mem={atoms.maxmem}B\n%chk={randString()}.chk\n#p force b3lyp/6-31g(d)\n\ngase\n\n{atoms.charge} {atoms.multiplicity}\n{atoms.get_symbols_positions()}{atoms.calc.connectivity}{atoms.calc.genecp}',
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
            r'\n (1[\\|\|]1[\\|\|][\s\S]*?[\\|\|][\\|\|])@\n': {
                # 'debug' : True,
                'important' : True,
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
            r'and normal coordinates:([\s\S]*?)\n ---[\s\S]*?Thermochemistry' : {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: gaussian_extract_frequency(data, arrays),
                'key' : 'frequency',
                },
            r' The second derivative matrix:\n([\s\S]*?)\n ITU' : {
                'important' : False,
                'selection' : -1,
                'process' : lambda data, arrays: gaussian_extract_hessian(data, arrays),
                'key' : 'Hessian',
                },
            },
        'synthesized_data' : OrderedDict({
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
                'equation' : lambda arrays: arrays['gaussian_datablock'][1],
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
                'prerequisite' : ['calc_arrays/results'],
                'equation' : lambda arrays: float(get_value_by_order(arrays['calc_arrays/results'], ENERGY_ORDER)) *\
                                            atomtools.unit.trans_energy('au', 'eV'),
                },
            'calc_arrays/zero_point_energy' : {
                'prerequisite' : ['calc_arrays/results/ZeroPoint'],
                'equation' : lambda arrays: float(arrays['calc_arrays/results/ZeroPoint']) *\
                                            atomtools.unit.trans_energy('au', 'eV'),
                },
            }),
    },
}

