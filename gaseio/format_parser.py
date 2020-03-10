"""
format parser from gase
"""


import os
import re
import configparser
import numpy as np
import atomtools.fileutil
import atomtools.filetype
import logging
import json_tricks
import dill as dill_pickle

# from .ext_types import ExtList
from .ext_types import ExtDict
from .ext_methods import astype, xml_parameters, datablock_to_numpy,\
    datablock_to_numpy, construct_depth_dict, \
    get_depth_dict, FileFinder, update_key, update_dict, has_key
from . import ext_methods
from .regularize import regularize_arrays


BASEDIR = os.path.dirname(os.path.abspath(__file__))


logging.basicConfig()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def read(fileobj, index=-1, format=None, warning=False, debug=False):
    from .format_string import FORMAT_STRING
    assert isinstance(index, int) or isinstance(index, slice)
    orig_index = index
    if isinstance(index, int):
        index = slice(index, None, None)
    all_file_string = atomtools.fileutil.get_file_content(fileobj)
    # fileobj.seek(0)
    file_format = format or atomtools.filetype.filetype(fileobj)
    # if file_format == 'json':
    #     string = fileobj.read()
    #     logger.debug(f"string: {all_file_string}")
    #     arrays = json_tricks.loads(all_file_string)
    #     logger.debug(f"orig_index: {orig_index}")
    #     logger.debug(f"index: {index}")
    #     if isinstance(arrays, dict):
    #         regularize_arrays(arrays)
    #     elif isinstance(arrays, list):
    #         [regularize_arrays(_arr) for _arr in arrays]
    #         if isinstance(orig_index, int):
    #             arrays = arrays[orig_index]
    #         else:
    #             arrays = arrays[index]
    #     logger.debug(f"{arrays}")
    #     logger.debug(f"type: {type(arrays)}")
    #     return arrays

    assert file_format is not None, \
        'format: {0}, fileobj {1}, file_format {2}'.format(
            format, fileobj, file_format)

    format_dict = FORMAT_STRING.get(file_format, None)
    if format_dict is None:
        raise NotImplementedError(f"{file_format} not available now")

    filename = atomtools.fileutil.get_absfilename(fileobj)

    if format_dict.get('parser_type', 'standard') == 'customized':
        parser = format_dict.get('parser')
        arrays = parser(all_file_string, index)
        if isinstance(arrays, list):
            arrays = arrays[index]

    # elif format_dict.get('file_format', None) == 'dict':
    #     ignorance = format_dict.get('ignorance', None)
    #     conf = configparser.ConfigParser(inline_comment_prefixes=ignorance)
    #     header = format_dict.get('file_format', 'default')
    #     conf.read_string('[vasp]\n' + all_file_string)
    #     return conf._sections

    else:
        file_string_sections = [all_file_string]
        if format_dict.get('multiframe', False):
            file_string_sections = re.findall(
                format_dict.get('frame_spliter'), all_file_string)
        frame_indices = range(len(file_string_sections))[index]
        file_string_sections = file_string_sections[index]
        all_arrays = []
        for frame_i, file_string in zip(frame_indices, file_string_sections):
            arrays = dict()
            arrays['filename'] = os.path.basename(
                filename) if filename else None
            arrays['frame_i'] = frame_i
            process_primitive_data(arrays, file_string,
                                   format_dict, warning, debug)
            if format_dict.get('primitive_data_function', None):
                format_dict.get('primitive_data_function')(file_string, arrays)
            process_synthesized_data(arrays, format_dict, debug)
            process_calculator(arrays, format_dict, debug)
            # if not show_file_content:
            #     del arrays['absfilename'], arrays['basedir']
            all_arrays.append(arrays)
        arrays = all_arrays
        if isinstance(orig_index, int):
            arrays = all_arrays[0]

    # regularize
    if not format_dict.get('non_regularize', False):
        if isinstance(arrays, dict):
            regularize_arrays(arrays)
        elif isinstance(arrays, list):
            for arr in arrays:
                regularize_arrays(arr)
    return arrays


def process_pattern(pattern, pattern_property, arrays, finder, warning=False, debug=False):
    """

    """
    # decode pattern_property
    if isinstance(pattern_property, bytes):
        pattern_property = dill_pickle.loads(pattern_property)

    key = pattern_property['key']
    important = pattern_property.get('important', False)
    selection = pattern_property.get('selection', -1)  # default select the last one
    results = {}

    if pattern_property.get('debug', False):
        import pdb
        pdb.set_trace()
    select_all = selection == 'all'

    assert isinstance(
        selection, int) or selection == 'all', 'selection must be int or all'
    match = finder.find_pattern(pattern)

    if not match:
        if important:
            raise ValueError(key, 'not match, however important')
        elif warning:
            print(' WARNING: ', key, 'not matched', '\n')
        return None

    if pattern_property.get('join', None):
        match = [pattern_property['join'].join(match)]
    process = pattern_property.get('process', None)
    if not select_all:
        match = [match[selection]]
    if process:
        match = [process(x, arrays) for x in match]
    if isinstance(key, str):
        value = match[0] if not select_all else match
        if pattern_property.get('type', None):
            if isinstance(value, np.ndarray):
                value = value.astype(pattern_property['type'])
            # elif isinstance(value, list):
            #     value = [pattern_property['type'](_) for _ in value]
            else:
                value = pattern_property['type'](value)
        if value is not None:
            # results.update(construct_depth_dict(key, value, arrays))
            update_key(results, key, value)
    else:  # array
        key_groups = key

        def np_select(data, dtype, index):
            try:
                data = eval('data[{0}]'.format(index))
            except IndexError:
                return None
            # print(all(data.shape))
            if isinstance(data, np.ndarray) and not all(data.shape):  # if contains no data
                return None
            if dtype is not None:
                return data.astype(dtype)
            return data
        for key_group in key_groups:
            key, dtype, index = key_group.get('key'), key_group.get(
                'type', None), key_group.get('index')
            if key_group.get('debug', False):
                import pdb
                pdb.set_trace()
            if not select_all:
                value = np_select(match[0], dtype, index)
            else:
                value = [np_select(data, dtype, index) for data in match]
            if value is None:
                continue
            if key_group.get('process', None):
                value = key_group.get('process')(value, arrays)
            if value is None or isinstance(value, np.ndarray) and (value == None).all():
                continue
            # results.update(construct_depth_dict(key, value, arrays))
            update_key(results, key, value)
    return results


def process_primitive_data(arrays, file_string, formats, warning=False, debug=False):
    from multiprocessing import Pool

    warning = warning or debug
    primitive_data, ignorance = formats['primitive_data'], formats.get(
        'ignorance', None)
    if isinstance(ignorance, tuple):
        file_string = '\n'.join([line for line in file_string.split('\n')
                                 if not (line.strip() and line.strip()[0] in ignorance)])
    # elif isinstance(ignorance, )
    file_format = formats.get('file_format', 'plain_text')
    finder = FileFinder(file_string, file_format=file_format)
    completed_keys = []
    completed_pattern = []


    def pattern_disallow(pattern_property, completed_keys):
        prerequisite = pattern_property.get('prerequisite', None)
        if not prerequisite:
            return False
        for _ in prerequisite:
            if not _ in completed_keys:
                return True
        return False


    processes = 4
    with Pool(processes=processes) as executor:
        handles = []
        while len(completed_pattern) < len(primitive_data.keys()):
            for pattern, pattern_property in primitive_data.items():
                if pattern in completed_pattern:
                    continue
                if pattern_disallow(pattern_property, completed_keys):
                    continue
                completed_pattern.append(pattern)
                args = (pattern, dill_pickle.dumps(pattern_property),
                        arrays, finder, warning, debug)
                if pattern_property.get("passerror", False):
                    try:
                        handles.append(executor.apply_async(process_pattern, args))
                    except:
                        pass
                else:
                    handles.append(executor.apply_async(process_pattern, args))
            for hdl in handles:
                results = hdl.get()
                # import pdb; pdb.set_trace()
                # arrays.update(results)
                if results:
                    update_dict(arrays, results)


def process_synthesized_data(arrays, formats, debug=False):
    """
    Process synthesized data
    """
    synthesized_data = formats.get('synthesized_data', None)
    if synthesized_data is None:
        return
    # print(synthesized_data)
    for key, key_property in synthesized_data.items():
        cannot_synthesize = False
        if key_property.get('debug', False):
            import pdb
            pdb.set_trace()
        if key_property.get('prerequisite', None):
            for item in key_property.get('prerequisite'):
                if isinstance(item, tuple):
                    has_key = False
                    for _item in item:
                        if ext_methods.has_key(arrays, _item):
                            has_key = True
                            break
                else:
                    has_key = True
                    if not ext_methods.has_key(arrays, item):
                        has_key = False
                if not has_key:
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


def process_calculator(arrays, formats_dict, debug=False):
    if 'calculator' in formats_dict:
        if not 'calc_arrays' in arrays:
            arrays['calc_arrays'] = dict()
        arrays['calc_arrays']['name'] = formats_dict.get('calculator')


def setdebug():
    logger.setLevel(logging.DEBUG)
