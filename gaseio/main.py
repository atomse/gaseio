"""
gaseio
"""


import os
import re
import logging


import atomtools.fileutil
import atomtools.name
import atomtools.filetype

logging.basicConfig()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def read(fileobj, index=-1, format=None, parallel=True, force_ase=False,
         force_gase=False, **kwargs):
    logger.debug(f"fileobj: {fileobj}")
    fileobj = atomtools.fileutil.get_uncompressed_fileobj(fileobj)
    _filetype = format or atomtools.filetype.filetype(fileobj)
    assert isinstance(index, int) or \
        re.match(r'^[+-:0-9]+$', str(index))
    if isinstance(index, str):
        if not ':' in index:
            index = int(index)
        else:
            start, stop, step = ([None if not _ else int(_)
                                  for _ in index.split(':')] + [None, None, None])[:3]
            index = slice(start, stop, step)
    if force_gase:
        return gase_reader(fileobj, index, _filetype, parallel, **kwargs)
    elif force_ase:
        return ase_reader(fileobj, index, format, parallel, **kwargs)
    else:
        try:
            return gase_reader(fileobj, index, _filetype, parallel, **kwargs)
        except:
            return ase_reader(fileobj, index, format, parallel, **kwargs)


def ase_reader(fileobj, index=None, format=None, parallel=True, **kwargs):
    from ase.io import read
    filename = atomtools.fileutil.get_filename(fileobj)
    # format = format or atomtools.filetype(filename)
    _atoms = read(fileobj, index, format, parallel, **kwargs)
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
    print('write', format)
    string = get_write_content(fileobj, images, format, parallel, append,
                               force_ase=force_ase, force_gase=force_gase, **kwargs)
    if preview:
        print(string)
    else:
        with open(fileobj, 'w') as fd:
            fd.write(string)


def get_write_content(fileobj, images, format=None, parallel=True, append=False,
                      force_ase=False, force_gase=False, preview=False, **kwargs):
    _filetype = format or atomtools.filetype.filetype(fileobj)
    print(_filetype)
    if force_gase:
        return gase_writer_content(images, _filetype)
    elif force_ase:
        return ase_writer_content(images, format, parallel, append, **kwargs)
    else:
        try:
            return gase_writer_content(images, _filetype)
        except Exception as e:
            return ase_writer_content(images, format, parallel, append, **kwargs)


def ase_writer_content(images, format=None, parallel=True, append=False,
                       force_ase=False, force_gase=False, preview=False, **kwargs):
    from ase.io import write
    _tmp_filename = '/tmp/%s' % (atomtools.name.randString())
    write(_tmp_filename, images, format, parallel, append, **kwargs)
    with open(_tmp_filename) as fd:
        string = fd.read()
    os.remove(_tmp_filename)
    return string


def gase_writer_content(images, _filetype):
    from .gase_writer import generate_input_content
    return generate_input_content(images, _filetype)


def write_preview(fileobj, images, format=None, parallel=True, append=False,
                  force_ase=False, force_gase=False, preview=False, **kwargs):
    preview(fileobj, images, format, parallel, append, force_ase=force_ase, force_gase=force_gase,
            preview=True, **kwargs)


def preview(images, format=None, force_ase=False, force_gase=False):
    write('-', images, format, force_ase=force_ase,
          force_gase=force_gase, preview=True)


def list_supported_write_formats(dtype=None):
    from . import gase_writer
    types_list = gase_writer.list_supported_write_formats()
    if dtype == 'string':
        return ' '.join(types_list)
    return types_list


def setdebug():
    logger.setLevel(logging.DEBUG)
