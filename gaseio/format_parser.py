"""
format parser from gase
"""


import os
import re
import configparser
import numpy as np
import atomtools

from .filetype import filetype
from .ext_types import ExtList, ExtDict
from .ext_methods import astype, xml_parameters, datablock_to_numpy,\
                         datablock_to_numpy, construct_depth_dict, \
                         get_depth_dict, FileFinder
from .regularize import regularize_arrays



BASEDIR = os.path.dirname(os.path.abspath(__file__))




def read(fileobj, index=-1, format=None, show_file_content=False, warning=False, debug=False):
    from .format_string import FORMAT_STRING
    assert isinstance(index, int) or isinstance(index, slice)
    orig_index = index
    if isinstance(index, int):
        index = slice(index, None, None)
    all_file_string = atomtools.file.get_file_content(fileobj)
    file_format = format or filetype(fileobj)

    assert file_format is not None
    format_dict = FORMAT_STRING.get(file_format, None)
    if format_dict is None:
        raise NotImplementedError(file_format, 'not available now')
    filename = atomtools.file.get_absfilename(fileobj)
    
    if format_dict.get('file_format', None) == 'dict':
        conf = configparser.ConfigParser()
        conf.read_string('[vasp]\n' + all_file_string)
        return conf._sections

    file_string_sections = [all_file_string]
    if format_dict.get('multiframe', False):
        file_string_sections = re.findall(format_dict.get('frame_spliter'), all_file_string)
    frame_indices = range(len(file_string_sections))[index]
    file_string_sections = file_string_sections[index]
    all_arrays = []
    for frame_i, file_string in zip(frame_indices, file_string_sections):
        arrays = ExtDict()
        arrays['absfilename'] = filename if filename else None
        arrays['basedir'] = os.path.basename(filename) if filename else None
        arrays['frame_i'] = frame_i
        process_primitive_data(arrays, file_string, format_dict, warning, debug)
        process_synthesized_data(arrays, format_dict, debug)
        process_calculator(arrays, format_dict, debug)
        if not show_file_content:
            del arrays['absfilename'], arrays['basedir']
        if not format_dict.get('non_regularize', False):
            regularize_arrays(arrays)
        all_arrays.append(arrays)
    if isinstance(orig_index, int):
        return all_arrays[0]
    return all_arrays[index]


def process_pattern(pattern, pattern_property, arrays, finder, warning=False, debug=False):
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
        return

    if pattern_property.get('join', None):
        match = [pattern_property['join'].join(match)]
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
        key_groups = key
        def np_select(data, dtype, index):
            try:
                data = eval('data[{0}]'.format(index))
            except IndexError:
                return None
            # print(all(data.shape))
            if isinstance(data, np.ndarray) and not all(data.shape): # if contains no data
                return None
            if dtype is not None:
                return data.astype(dtype)
            return data
        for key_group in key_groups:
            key, dtype, index = key_group.get('key'), key_group.get('type', None), key_group.get('index')
            if key_group.get('debug', False):
                import pdb; pdb.set_trace()
            if not selectAll:
                value = np_select(match[0], dtype, index)
            else:
                value = [np_select(data, dtype, index) for data in match]
            if value is None:
                continue
            if key_group.get('process', None):
                value = key_group.get('process')(value, arrays)
            arrays.update(construct_depth_dict(key, value, arrays))


def process_primitive_data(arrays, file_string, formats, warning=False, debug=False):
    warning = warning or debug
    primitive_data, ignorance = formats['primitive_data'], formats.get('ignorance', None)
    if isinstance(ignorance, tuple):
        file_string = '\n'.join([line for line in file_string.split('\n') \
            if not (line.strip() and line.strip()[0] in ignorance)])
    # elif isinstance(ignorance, )
    file_format = formats.get('file_format', 'plain_text')
    finder = FileFinder(file_string, file_format=file_format)
    for pattern, pattern_property in primitive_data.items():
        if pattern_property.get("passerror", False):
            try:
                process_pattern(pattern, pattern_property, arrays, finder, warning, debug)
            except:
                pass
        else:
            process_pattern(pattern, pattern_property, arrays, finder, warning, debug)

def process_synthesized_data(arrays, formats, debug=False):
    """
    Process synthesized data
    """
    synthesized_data = formats.get('synthesized_data', None)
    if synthesized_data is None:
        return
    for key, key_property in synthesized_data.items():
        cannot_synthesize = False
        if key_property.get('debug', False):
            import pdb; pdb.set_trace()
        if key_property.get('prerequisite', None):
            for item in key_property.get('prerequisite'):
                if not arrays.has_key(item):
                    cannot_synthesize = True
        condition = key_property.get('condition', None)
        if condition and not condition(arrays):
            cannot_synthesize = True
        if not cannot_synthesize:
            equation = key_property['equation']
            value = equation(arrays)
            if key_property.get('process', None):
                value = key_property.get('process')(value, arrays)
            arrays.update(construct_depth_dict(key, value, arrays))
        if key_property.get('delete', None):
            for item in key_property.get('delete'):
                if item in arrays:
                    del arrays[item]


def process_calculator(arrays, formats, debug=False):
    if 'calculator' in formats:
        arrays['calculator'] = formats.get('calculator')


