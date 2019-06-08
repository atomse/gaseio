"""
format parser from gase
"""


import os
import re
import glob

from io import StringIO

import numpy as np
import pandas as pd

# try:
#     from gase import Atoms
#     import gase.calculators as calculators
#     HAS_GASE = True
# except ModuleNotFoundError:
#     HAS_GASE = False

import atomtools
from .filetype import filetype
from .ext_types import ExtList, ExtDict
from .ext_methods import astype, xml_parameters, datablock_to_numpy,\
                         datablock_to_numpy, construct_depth_dict, \
                         get_depth_dict, FileFinder


BASEDIR = os.path.dirname(os.path.abspath(__file__))




def read(fileobj, format=None, get_dict=False, warning=False, debug=False):
    from .format_string import FORMAT_STRING
    # file_string, file_format = get_filestring_and_format(fileobj, format)
    file_string = atomtools.file.get_file_content(fileobj)
    file_format = format or filetype(fileobj)

    assert file_format is not None
    formats = FORMAT_STRING[file_format]
    arrays = ExtDict()
    arrays['basedir'] = ''
    filename = atomtools.file.get_filename(fileobj)
    if filename:
        arrays['basedir'] = os.path.dirname(filename)

    process_primitive_data(arrays, file_string, formats, warning, debug)
    process_synthesized_data(arrays, formats, debug)
    return arrays
    # if not HAS_GASE or get_dict:
    #     return arrays
    # return assemble_atoms(arrays, formats.get('calculator', None))

def process_primitive_data(arrays, file_string, formats, warning=False, debug=False):
    warning = warning or debug
    primitive_data, ignorance = formats['primitive_data'], formats.get('ignorance', None)
    if ignorance:
        file_string = '\n'.join([line.strip() for line in file_string.split('\n') \
            if not (line and line[0] in ignorance)])
    file_format = formats.get('file_format', 'plain_text')
    finder = FileFinder(file_string, file_format=file_format)
    for pattern, pattern_property in primitive_data.items():
        if debug:
            print(pattern, pattern_property)
        key = pattern_property['key']
        important = pattern_property.get('important', False)
        selection = pattern_property.get('selection', -1) # default select the last one
        if pattern_property.get('debug', False):
            import pdb; pdb.set_trace()
        selectAll = selection == 'all'
        assert isinstance(selection, int) or selection == 'all', 'selection must be int or all'
        match = finder.find_pattern(pattern)
        if not match:
            if important:
                raise ValueError(key, 'not match, however important')
            elif warning:
                print(' WARNING: ', key, 'not matched', '\n')
            continue
        if pattern_property.get('join', None):
            match = [pattern_property['join'].join(match)]
            # import pdb; pdb.set_trace()
        process = pattern_property.get('process', None)
        if not selectAll:
            match = [match[selection]]
        if process:
            match = [process(x, arrays) for x in match]
        if isinstance(key, str):
            value = match[0] if not selectAll else match
            if pattern_property.get('type', None):
                if isinstance(value, np.ndarray):
                    value = value.astype(pattern_property['type'])
                else:
                    value = pattern_property['type'](value)
            arrays.update(construct_depth_dict(key, value, arrays))
        else: # array
            def np_select(data, dtype, index):
                data = eval('data[{0}]'.format(index))
                return data.astype(dtype)
            for key_group in key:
                key, dtype, index = key_group['key'], key_group['type'], key_group['index']
                if not selectAll:
                    value = np_select(match[0], dtype, index)
                else:
                    value = [np_select(data, dtype, index) for data in match]
                arrays.update(construct_depth_dict(key, value, arrays))

def process_synthesized_data(arrays, formats, debug=False):
    # Process synthesized data
    synthesized_data = formats['synthesized_data']
    for key, key_property in synthesized_data.items():
        cannot_synthesize = False
        if key_property.get('debug', False):
            import pdb; pdb.set_trace()
        if key_property.get('prerequisite', None):
            for item in key_property.get('prerequisite'):
                if not arrays.has_key(item):
                    cannot_synthesize = True
        if cannot_synthesize:
            continue
        equation = key_property['equation']
        value = equation(arrays)
        arrays.update(construct_depth_dict(key, value, arrays))
        if key_property.get('delete', None):
            for item in key_property.get('delete'):
                del arrays[item]

# def assemble_atoms(arrays, calculator):
#     assert HAS_GASE
#     if arrays.get('unit', None):
#         arrays['positions'] *= atomtools.unit.trans_length(arrays['unit'], 'Ang')
#         del arrays['unit']
#     if arrays.get('numbers', None) is not None:
#         symbols = arrays.get('numbers')
#     else:
#         symbols = ''.join(arrays['symbols'])
#     _atoms = Atoms(symbols=symbols, positions=arrays['positions'])
#     if calculator:
#         _atoms.calc = getattr(calculators, calculator)()
#     for key, val in arrays.items():
#         if key in ['symbols', 'positions']:
#             continue
#         setattr(_atoms, key, val)
#     return _atoms

def writer(atoms, format=None):
    from .format_string import FORMAT_STRING
    assert format is not None
    _format = FORMAT_STRING[format]['writer_formats']
    _fstring = '''f%r ''' %(_format)
    string = eval(_fstring)
    return string


def get_obj_value(obj, key, dict_sep=' '):
    assert isinstance(key, tuple)
    if not isinstance(key[0], tuple):
        name, _type = key
        val = get_depth_dict(obj, name)
        if val is not None:
            if _type in [int, float]:
                val = _type(val)
            elif _type in [dict]:
                val = '{0}{1}{2}'.format(name, dict_sep, val)
    else:
        arrays = None
        for subkey, subtype, idx in key:
            val = get_depth_dict(obj, subkey)
            if isinstance(val, list):
                val = np.array(val)
            if val.ndim == 1:
                val = val.reshape((-1, 1))
            if arrays is None:
                arrays = val
            else:
                arrays = np.hstack([arrays, val])
        val = pd.DataFrame(arrays).to_string(header=None, index=None)
    return val

def template(atoms, template_file=None, format=None, print_mode=False):
    from .format_string import FORMAT_STRING
    if template_file is None:
        template_file = glob.glob('{0}/base_format/{1}.*'.format(BASEDIR, format))[0]
    # template_file, format = get_filestring_and_format(template_file, format)
    template_file_content = atomtools.file.get_file_content(template_file)
    format = format or filetype(template_file)
    assert format is not None
    reader_formats = FORMAT_STRING[format]['reader_formats']
    for pattern, pattern_property in reader_formats.items():
        key_group, important = pattern_property['groups'], pattern_property['important']
        match = re.match(pattern, template_file)
        if match is None:
            if important:
                raise ValueError(key_group, 'not match, however important')
            continue
        vals = match.groups()
        # start = match.start()
        newval = None
        for i, (key, val) in enumerate(zip(key_group, vals)):
            start = match.start(i+1)
            newval = get_obj_value(atoms, key)
            if newval is not None:
                # print(start, key, '\n', val, '\n', newval, '\n', template_file.index(val))
                if val[-1] == '\n' and newval[-1] != '\n':
                    newval += '\n'
                template_file = template_file[:start] + \
                    template_file[start:].replace(val, str(newval), 1)
                match = re.match(pattern, template_file)
        # if newval is not None:
    if not print_mode:
        return template_file
    print(template_file)


def get_template(fileobj, format=None):
    format = format or filetype(fileobj)
    assert format is not None

def test():
    from .format_string import FORMAT_STRING
    for _filetype in FORMAT_STRING:
        filenames = glob.glob('{0}/base_format/{1}.*'.format(BASEDIR, _filetype))
        if not filenames:
            continue
        # print(filenames, _filetype)
        filename = filenames[0]
        print('\n', _filetype)
        _dict = read(filename, format=_filetype, get_dict=True, warning=True)
        print(_dict)
        if _filetype == 'gaussian':
            print(_dict.get('connectivity', None))
        print(read(filename, format=_filetype, ))
    # _atoms = Atoms('C6H6', positions=np.random.rand(12, 3))
    # for _filetype in FORMAT_STRING:
    #     print('\n\n\n ======= ', _filetype)
    #     template(_atoms, format=_filetype, print_mode=True)




if __name__ == '__main__':
    test()
