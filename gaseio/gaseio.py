"""
gaseio
"""


import os
import ase.io
import atomtools

from .filetype import filetype




BASEDIR = os.path.dirname(os.path.abspath(__file__))



def read(fileobj, index=None, format=None, parallel=True, force_ase=False, 
         force_fmt=False, **kwargs):
    if force_fmt:
        return fmt_reader(fileobj, index, format, parallel, **kwargs)
    elif force_ase:
        return ase_reader(fileobj, index, format, parallel, **kwargs)
    else:
        try:
            return fmt_reader(fileobj, index, format, parallel, **kwargs)
        except:
            return ase_reader(fileobj, index, format, parallel, **kwargs)


def ase_reader(fileobj, index=None, format=None, parallel=True, **kwargs):
    filename = atomtools.file.get_filename(fileobj)
    format = format or filetype(filename)
    _atoms = ase.io.read(fileobj, index, format, parallel, **kwargs)
    return gase.Atoms(arrays=_atoms.arrays)


def fmt_reader(fileobj, index=None, format=None, parallel=True, **kwargs):
    from . import format_parser
    return format_parser.read(fileobj, format=format, **kwargs)


def read_preview(fileobj, lines=200):
    """
    show last `lines` lines of fileobj, default 200 lines
    """
    string = ''.join(fd.read().split('\n')[-200:])
    with open(fileobj) as fd:
        print(string)


def write(fileobj, images, format=None, parallel=True, append=False, **kwargs):
    string = _preview(fileobj, images, format, parallel, append, **kwargs)
    with open(fileobj, 'w') as fd:
        fd.write(string)


def _preview(fileobj, images, format=None, parallel=True, append=False, **kwargs):
    format = format or filetype(fileobj)
    _fileobj = '/tmp/%s' %(atomtools.name.randString())
    _writer = ase.io.write
    if format in types_custom:
        mode, _reader, _writer = types_custom[format]
    _writer(_fileobj, images, append, **kwargs)
    with open(_fileobj) as fd:
        string = fd.read()
    os.remove(_fileobj)
    return string

def preview(fileobj, images, format=None, parallel=True, append=False, **kwargs):
    print(_preview(fileobj, images, format, parallel, append, **kwargs))


def test(test_types=None):
    test_dir = os.path.join(BASEDIR, 'testcases')
    for filename in os.listdir(test_dir):
        if filename.startswith('.'):
            continue
        filename = os.path.join(test_dir, filename)
        print(filename)
        if os.path.isfile(filename):
            print(read(filename, force_fmt=True, debug=True))
