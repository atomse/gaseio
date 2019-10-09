"""
format parser from gase
"""
import os
import re
from lxml import etree
import glob
import collections
import copy

from io import StringIO
from typing import Pattern

import math
import numpy as np
import pandas as pd

import chemdata
import atomtools.fileutil
import atomtools.string
import atomtools.filetype


# from .ext_types import ExtList, ExtDict


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def astype(typestring):
    if typestring in [int, float, str, bool]:
        return typestring
    typestring = typestring.lower()
    if typestring == 'int':
        return int
    elif typestring == 'float':
        return float
    elif typestring == 'string':
        return str
    elif typestring == 'logical':
        return bool
    else:
        raise NotImplementedError('{0} not implemented'.format(typestring))


def update_items_with_node(root, item_xpath=None, default_type='float', sdict=dict()):
    item_xpath = item_xpath or ['./i', './v']
    if isinstance(item_xpath, str):
        item_xpath = [item_xpath]
    assert isinstance(item_xpath, (list, tuple)
                      ), 'xpath {0} should be a list'.format(item_xpath)
    item_xpath = '|'.join(item_xpath)
    for item_node in root.xpath(item_xpath):
        item_name = item_node.get('name')
        item_type = item_node.get('type', default_type)
        text = item_node.text
        if text is None:
            continue
        elif text == '*' * len(text):
            value = atomtools.string.STRING_OVERFLOW
        else:
            if item_node.tag == 'i':
                value = astype(item_type)(item_node.text)
            elif item_node.tag == 'v':
                value = datablock_to_numpy(
                    item_node.text).flatten().astype(astype(item_type))
            else:
                raise NotImplementedError(
                    '{0} not implemeneted in xml update items'.format(item_node.tag))
        sdict.update({item_name: value})
    return sdict


def update(orig_dict, new_dict):
    if isinstance(orig_dict, tuple):
        return copy.copy(orig_dict)
    for key, val in new_dict.items():
        if isinstance(val, collections.Mapping):
            tmp = update(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict.get(key, []) + val)
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict


def xml_parameters(xml_node):
    parameters = {}
    parameters_section = {}
    ITEM_XPATH = ['./v', './i']
    for sep_node in xml_node.xpath('./separator'):
        sep_name = sep_node.get('name')
        sdict = update_items_with_node(sep_node, item_xpath=ITEM_XPATH)
        parameters_section.update({sep_name: list(sdict)})
        parameters.update(sdict)
    sdict = update_items_with_node(xml_node, item_xpath=ITEM_XPATH)
    parameters_section.update({'root': list(sdict)})
    parameters.update(sdict)
    # parameters['SECTION_DATA'] = parameters_section
    return parameters


def datablock_to_dataframe(datablock, sep=r'\s+', header=None):
    """
    datablock is a string that contains a block of data
    """
    assert isinstance(datablock, str)
    return pd.read_csv(StringIO(datablock), header=header, sep=sep, index_col=None,
                       error_bad_lines=False, warn_bad_lines=False)


def datablock_to_numpy(datablock, sep=r'\s+', header=None):
    """
    datablock is a string that contains a block of data
    """
    return datablock_to_dataframe(datablock, sep, header).values


def datablock_to_numpy_extend(datablock, sep=r'\s+', header=None):
    """
    datablock is a string that contains a block of data
    """
    if not header:
        max_width = 0
        for line in datablock.split('\n'):
            if len(line.split()) > max_width:
                max_width = len(line.split())
        header_line = ' '.join([str(i) for i in range(max_width)])
        datablock = header_line + '\n' + datablock
        header = 0
    return datablock_to_dataframe(datablock, sep, header).values


def datablock_to_numpy_fixed_width(datablock, colspecs, header=None, nan_fill=None):
    """
    https://stackoverflow.com/questions/4914008/how-to-efficiently-parse-fixed-width-files
    """
    df = pd.read_fwf(StringIO(datablock), colspecs=colspecs, header=header)
    df = df.where((pd.notnull(df)), None)
    return df.values


def datablock_to_dict(datablock, sep=r'\s*=\s*', dtype=float):
    rsdict = {}
    # print(datablock)
    for line in datablock.strip().split('\n'):
        item_val = re.split(re.compile(sep), line.strip())
        # print(item_val)
        item, val = item_val
        rsdict[item] = dtype(val)
    return rsdict


def construct_depth_dict(names, value, root=None):
    names = names.split('/')
    root = root or {}
    ptr = root
    for name in names[:-1]:
        if not name in ptr:
            ptr[name] = {}
        ptr = ptr[name]
    ptr[names[-1]] = value
    return root


def get_depth_dict(root, names):
    names = names.split('/')
    ptr = root
    for name in names:
        if isinstance(ptr, dict):
            if not name in ptr:
                return None
            ptr = ptr[name]
        else:
            ptr = getattr(ptr, name, None)
            if ptr is None:
                return None
    return ptr


def string_to_dict(string, sep='|', keysep='='):
    sdict = dict()
    for keyval in string.split(sep):
        # print(string, keyval)
        key, val = keyval.split(keysep)
        sdict[key] = val
    return sdict


def substitute_with_define(string, def_val=None, block_by_block=True):
    # import pdb; pdb.set_trace()
    pattern = re.compile(
        r'\b(cos|sin|tan|cot|sqr|sqrt|pi)\b',  flags=re.IGNORECASE)
    string = re.sub(pattern, lambda m: 'math.'+m.group(0).lower(), string)
    if def_val is not None:
        assert isinstance(def_val, dict)
        for _name, _val in def_val.items():
            string = re.sub(r'\b{0}\b'.format(_name), str(_val), string)
    # evaluate each line&block in string
    if block_by_block:
        lines = string.split('\n')
        for line_i, line in enumerate(lines):
            blocks = line.split()
            for i, block in enumerate(blocks):
                try:
                    blocks[i] = eval(block)
                except:
                    pass
            lines[line_i] = ' '.join(str(_) for _ in blocks)
        string = '\n'.join(lines)
    return string


def process_defines(defines, def_val=None):
    # defines = re.sub(r'\b(cos|sin|tan|cot|sqr|sqrt)\b', 'math.\g<1>', defines)
    if isinstance(defines, tuple):
        defines = defines[0]
    if def_val is None:
        def_val = {}
    for line in defines.split('\n'):
        name, val = re.split(r'\s*=\s*', line)
        name = name.strip()
        val = val.strip()
        val = substitute_with_define(val, def_val, block_by_block=False)
        def_val[name] = eval(val)
    return def_val


def regularize_cell(cell):
    cell = np.array(cell).flatten()
    if cell.shape == (3,):
        cell = np.diag(cell)
    cell = cell.reshape((-1, 3))
    assert cell.shape == (3, 3)
    return cell


def process_blockdata_with_several_lines(data, ndim_length_regex, rm_header_regex, index_length, dtype='square'):
    # import pdb; pdb.set_trace()
    assert dtype in ['square', 'lower_triangular']
    data_ndim = re.findall(ndim_length_regex, data)[0].strip()
    ndim = data_ndim.count('\n') + 1
    data = re.sub(rm_header_regex, '\n', data).strip()

    lines = [_[index_length:] for _ in data.split('\n')]
    max_width = max([len(_.split()) for _ in lines])
    if dtype == 'square':
        for i in range(ndim):
            lines[i] = ' '.join(lines[i::ndim])
        header = ' '.join(str(_) for _ in range(len(lines[0].split())))
    elif dtype == 'lower_triangular':
        block_length = ndim % max_width
        end_point = 0
        while block_length < ndim:
            for i in range(1, block_length+1):
                x1 = (end_point+i+block_length)
                x2 = (end_point+i)
                # print(len(lines), x2, x1, block_length, end_point)
                lines[-x1] += ' ' + lines[-x2]
            end_point += block_length
            block_length += max_width
        header = ' '.join(str(_) for _ in range(ndim))
    newdata = header + '\n' + '\n'.join(lines[:ndim])
    # print('newdata', newdata)
    outdata = datablock_to_numpy(newdata, header=0)
    if dtype != 'square':
        # print(outdata)
        outdata[np.isnan(outdata)] = 0
        outdata += np.triu(outdata.T, 1)
    return outdata


class FileFinder(object):
    """docstring for FileFinder"""
    SUPPOTED_FILETYPE = ['plain_text', 'lxml']

    def __init__(self, fileobj, file_format='plain_text'):
        super(FileFinder, self).__init__()
        self.fileobj = fileobj
        self.file_format = file_format
        file_string = atomtools.fileutil.get_file_content(fileobj)
        # print(fileobj)
        file_format = file_format or atomtools.filetype.filetype(fileobj)
        if not file_format in self.SUPPOTED_FILETYPE:
            raise NotImplementedError(
                'only {0} are supported'.format(self.SUPPOTED_FILETYPE))
        # assert isinstance(filename, str) and os.path.exists(filename), '{0} not exists'.format(filename)
        if file_format == 'plain_text':
            self.fileobj = file_string
        elif file_format == 'lxml':
            self.fileobj = etree.HTML(file_string.encode())

    def find_pattern(self, pattern):
        assert isinstance(pattern, (str, Pattern))
        if self.file_format == 'plain_text':
            return re.findall(pattern, self.fileobj)
        elif self.file_format == 'lxml':
            try:
                return self.fileobj.xpath(pattern)
            except:
                return None


def regularize_symbols(symbols):
    print(symbols)
    assert isinstance(symbols, (list, np.ndarray))
    sample = symbols[0]
    if isinstance(sample, (int, float)) or isinstance(sample, str) and sample.isdigit():
        symbols = [int(x) for x in symbols]
        symbols = [chemdata.chemical_symbols[x] for x in symbols]
    else:
        symbols = [symbol[0].upper() + symbol[1].lower() if len(symbol) >= 2 and symbol[:2].lower() in
                   [_.lower() for _ in chemdata.chemical_symbols]
                   else symbol[0].upper() for symbol in symbols]
    return symbols


def reshape_to_square(array):
    assert isinstance(array, np.ndarray)
    array = array.flatten()
    length = int(np.sqrt(len(array)))
    array = array.reshape((length, length))
    return array


def lower_diagnal_order_2_square(tri, dim=None):
    assert tri.ndim == 1
    if not dim:
        dim = int((tri.shape[0]*2) ** 0.5)
    assert tri.shape == (dim*(dim+1)/2,)
    square = np.zeros((dim, dim))
    id = np.tril_indices(dim)
    square[id] = tri
    square[id[::-1]] = tri
    return square


def parse_config_content(data, add_header=False, ignorance=('#',)):
    import configparser
    if add_header:
        header = 'tmpheader'
        data = "["+header+"]\n\n" + data
    conf = configparser.ConfigParser(inline_comment_prefixes=ignorance)
    conf.read_string(data)
    arrays = conf._sections
    if add_header:
        arrays = arrays[header]
    return arrays
