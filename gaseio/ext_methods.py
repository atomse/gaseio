"""
format parser from gase
"""
import os
import re
from lxml import etree
import glob

from io import StringIO
import numpy as np
import pandas as pd
from . import filetype

import atomtools
from .ext_types import ExtList, ExtDict


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
    assert isinstance(item_xpath, (list, tuple)), 'xpath {0} should be a list'.format(item_xpath)
    item_xpath = '|'.join(item_xpath)
    for item_node in root.xpath(item_xpath):
        item_name = item_node.get('name')
        item_type = item_node.get('type', default_type)
        if item_node.tag == 'i':
            value = astype(item_type)(item_node.text)
        elif item_node.tag == 'v':
            value = datablock_to_numpy(item_node.text).flatten().astype(astype(item_type))
        else:
            raise NotImplementedError('{0} not implemeneted in xml update items'.format(item_node.tag))
        sdict.update({item_name: value})
    return sdict

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


def datablock_to_numpy(datablock):
    """
    datablock is a string that contains a block of data
    """
    assert isinstance(datablock, str)
    return pd.read_csv(StringIO(datablock), header=None, sep=r'\s+', index_col=None).values

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


# def get_filestring_and_format(fileobj, file_format=None):
#     if hasattr(fileobj, 'read'):
#         fileobj = fileobj.read()
#     elif isinstance(fileobj, str):
#         if os.path.exists(fileobj):
#             file_format = file_format or filetype.filetype(fileobj)
#             fileobj = open(fileobj).read()
#     return fileobj.lstrip(), file_format


# def read(fileobj, format=None, get_dict=False, warning=False, DEBUG=False):
#     from .format_string import FORMAT_STRING
#     file_string, file_format = get_filestring_and_format(fileobj, format)
#     assert file_format is not None
#     formats = FORMAT_STRING[file_format]
#     arrays = ExtDict()
#     process_primitive_data(arrays, file_string, formats, warning, DEBUG)
#     process_synthesized_data(arrays, formats, DEBUG)
#     if not HAS_ATOMSE or get_dict:
#         return arrays
#     return assemble_atoms(arrays, formats.get('calculator', None))


class FileFinder(object):
    """docstring for FileFinder"""
    SUPPOTED_FILETYPE = ['plain_text', 'lxml']
    def __init__(self, fileobj, file_format='plain_text'):
        super(FileFinder, self).__init__()
        self.fileobj = fileobj
        self.file_format = file_format
        file_string = atomtools.file.get_file_content(fileobj)
        print(fileobj)
        file_format = file_format or filetype(fileobj)
        if not file_format in self.SUPPOTED_FILETYPE:
            raise NotImplementedError('only {0} are supported'.format(self.SUPPOTED_FILETYPE))
        # assert isinstance(filename, str) and os.path.exists(filename), '{0} not exists'.format(filename)
        if file_format == 'plain_text':
            self.fileobj = file_string
        elif file_format == 'lxml':
            self.fileobj = etree.HTML(file_string.encode())

    def find_pattern(self, pattern):
        assert isinstance(pattern, str)
        if self.file_format == 'plain_text':
            return re.findall(pattern, self.fileobj)
        elif self.file_format == 'lxml':
            return self.fileobj.xpath(pattern)

