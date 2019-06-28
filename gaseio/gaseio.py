"""
gaseio
"""


import os
import re
import atomtools

from .filetype import filetype




BASEDIR = os.path.dirname(os.path.abspath(__file__))



def read(fileobj, index=-1, format=None, parallel=True, force_ase=False, 
         force_gase=False, **kwargs):
    fileobj = atomtools.file.get_uncompressed_fileobj(fileobj)
    assert isinstance(index, int) or\
           re.match(r'^[+-:0-9]+$', str(index)) 
    if isinstance(index, str):
        if not ':' in index:
            index = int(index)
        else:
            start, stop, step = ([None if not _ else int(_) \
                                 for _ in index.split(':')] + [None, None, None])[:3]
            index = slice(start, stop, step)
    if force_gase:
        return gase_reader(fileobj, index, format, parallel, **kwargs)
    elif force_ase:
        return ase_reader(fileobj, index, format, parallel, **kwargs)
    else:
        try:
            return gase_reader(fileobj, index, format, parallel, **kwargs)
        except:
            return ase_reader(fileobj, index, format, parallel, **kwargs)


def ase_reader(fileobj, index=None, format=None, parallel=True, **kwargs):
    import ase.io
    filename = atomtools.file.get_filename(fileobj)
    format = format or filetype(filename)
    _atoms = ase.io.read(fileobj, index, format, parallel, **kwargs)
    return _atoms.arrays


def gase_reader(fileobj, index=-1, format=None, parallel=True, **kwargs):
    from . import format_parser
    return format_parser.read(fileobj, index=index, format=format, **kwargs)


def read_preview(fileobj, lines=200):
    """
    show last `lines` lines of fileobj, default 200 lines
    """
    with open(fileobj) as fd:
        string = ''.join(fd.read().split('\n')[-200:])
        print(string)


def write(fileobj, images, format=None, parallel=True, append=False, force_ase=False, 
          force_gase=False, preview=False, **kwargs):
    string = get_write_content(fileobj, images, format, parallel, append,
                                   force_ase=force_ase, force_gase=force_gase, **kwargs)
    if preview:
        print(string)
    else:
        with open(fileobj, 'w') as fd:
            fd.write(string)


def get_write_content(fileobj, images, format=None, parallel=True, append=False,
                          force_ase=False, force_gase=False, preview=False, **kwargs):
    from . import gase_writer
    import ase.io
    _tmp_filename = '/tmp/%s' %(atomtools.name.randString())
    _filetype = format or filetype(fileobj)
    if force_gase:
        gase_writer.generate_inputfile(images, _filetype, _tmp_filename)
    elif force_ase:
        ase.io.write(_tmp_filename, images, format, parallel, append, **kwargs)
    else:
        try:
            gase_writer.generate_inputfile(images, _filetype, _tmp_filename)
        except Exception as e:
            ase.io.write(_tmp_filename, images, format, parallel, append, **kwargs)
    with open(_tmp_filename) as fd:
        string = fd.read()
    os.remove(_tmp_filename)
    return string

def preview_write(fileobj, images, format=None, parallel=True, append=False,
                  force_ase=False, force_gase=False, preview=False, **kwargs):
    write(fileobj, images, format, parallel, append, force_ase=force_ase, force_gase=force_gase, preview=True, **kwargs)


