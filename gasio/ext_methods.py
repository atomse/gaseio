"""
format parser from atomse
"""
import os
import re
from lxml import etree
import glob

from io import StringIO
import numpy as np
import pandas as pd
from ase.io.formats import filetype
try:
    from atomse import Atoms
    import atomse.calculators as calculators
    HAS_ATOMSE = True
except ModuleNotFoundError:
    HAS_ATOMSE = False

from .units import unit_to_Ang
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


def get_filestring_and_format(fileobj, file_format=None):
    if hasattr(fileobj, 'read'):
        fileobj = fileobj.read()
    elif isinstance(fileobj, str):
        if os.path.exists(fileobj):
            file_format = file_format or filetype(fileobj)
            fileobj = open(fileobj).read()
    return fileobj.lstrip(), file_format


def read(fileobj, format=None, get_dict=False, warning=False, DEBUG=False):
    from .format_string import FORMAT_STRING
    file_string, file_format = get_filestring_and_format(fileobj, format)
    assert file_format is not None
    formats = FORMAT_STRING[file_format]
    arrays = ExtDict()
    process_primitive_data(arrays, file_string, formats, warning, DEBUG)
    process_synthesized_data(arrays, formats, DEBUG)
    if not HAS_ATOMSE or get_dict:
        return arrays
    return assemble_atoms(arrays, formats.get('calculator', None))


class FileFinder(object):
    """docstring for FileFinder"""
    SUPPOTED_FILETYPE = ['plain_text', 'lxml']
    def __init__(self, fileobj, file_format='plain_text'):
        super(FileFinder, self).__init__()
        self.fileobj = fileobj
        self.file_format = file_format
        file_string, file_format = get_filestring_and_format(fileobj, file_format)
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

def process_primitive_data(arrays, file_string, formats, warning=False, DEBUG=False):
    warning = warning or DEBUG
    primitive_data, ignorance = formats['primitive_data'], formats.get('ignorance', None)
    if ignorance:
        file_string = '\n'.join([line.strip() for line in file_string.split('\n') \
            if not (line and line[0] in ignorance)])
    file_format = formats.get('file_format', 'plain_text')
    finder = FileFinder(file_string, file_format=file_format)
    for pattern, pattern_property in primitive_data.items():
        if DEBUG: print(pattern, pattern_property)
        key = pattern_property['key']
        important = pattern_property.get('important', False)
        selection = pattern_property.get('selection', -1) # default select the last one
        selectAll = selection == 'all'
        assert isinstance(selection, int) or selection == 'all', 'selection must be int or all'
        match = finder.find_pattern(pattern)
        if DEBUG: print(match)
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
        if DEBUG:
            print('match', match)
        if not selectAll:
            match = [match[selection]]
        if process:
            match = [process(x, arrays) for x in match]
        if isinstance(key, str):
            value = match[0] if not selectAll else match
            if DEBUG: print(key, value)
            if pattern_property.get('type', None):
                if isinstance(value, np.ndarray):
                    value = value.astype(pattern_property['type'])
                else:
                    value = pattern_property['type'](value)
            arrays.update(construct_depth_dict(key, value, arrays))
        else: # array
            if DEBUG: print(key)
            def np_select(data, dtype, index):
                if DEBUG: print(data, type(data))
                data = eval('data[{0}]'.format(index))
                return data.astype(dtype)
            for key_group in key:
                key, dtype, index = key_group['key'], key_group['type'], key_group['index']
                if not selectAll:
                    value = np_select(match[0], dtype, index)
                else:
                    value = [np_select(data, dtype, index) for data in match]
                arrays.update(construct_depth_dict(key, value, arrays))

def process_synthesized_data(arrays, formats, DEBUG=False):
    # Process synthesized data
    synthesized_data = formats['synthesized_data']
    for key, key_property in synthesized_data.items():
        cannot_synthesize = False
        if key_property.get('prerequisite', None):
            for item in key_property.get('prerequisite'):
                if not item in arrays:
                    if DEBUG: print('{0} not in arrays, {1} cannot be synthesized'.format(item, key))
                    cannot_synthesize = True
        if cannot_synthesize:
            continue
        equation = key_property['equation']
        value = equation(arrays)
        arrays.update(construct_depth_dict(key, value, arrays))
        if key_property.get('delete', None):
            for item in key_property.get('delete'):
                del arrays[item]

def assemble_atoms(arrays, calculator):
    assert HAS_ATOMSE
    if arrays.get('unit', None):
        arrays['positions'] *= unit_to_Ang(arrays['unit'])
        del arrays['unit']
    if arrays.get('numbers', None) is not None:
        symbols = arrays.get('numbers')
    else:
        symbols = ''.join(arrays['symbols'])
    _atoms = Atoms(symbols=symbols, positions=arrays['positions'])
    if calculator:
        _atoms.calc = getattr(calculators, calculator)()
    for key, val in arrays.items():
        if key in ['symbols', 'positions']:
            continue
        setattr(_atoms, key, val)
    return _atoms

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
        template_file = glob.glob('{0}/base_format/{1}.*'.format(BASE_DIR, format))[0]
    template_file, format = get_filestring_and_format(template_file, format)
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
        filename = glob.glob('{0}/base_format/{1}.*'.format(BASE_DIR, _filetype))[0]
        print('\n', _filetype)
        _dict = read(filename, format=_filetype, get_dict=True, warning=True)
        print(_dict)
        if _filetype == 'gaussian':
            print(_dict.get('connectivity', None))
        print(read(filename, format=_filetype, ))
    _atoms = Atoms('C6H6', positions=np.random.rand(12, 3))
    for _filetype in FORMAT_STRING:
        print('\n\n\n ======= ', _filetype)
        template(_atoms, format=_filetype, print_mode=True)




if __name__ == '__main__':
    test()
