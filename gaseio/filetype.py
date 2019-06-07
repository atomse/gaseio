"""
analyze filetype 
"""


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_EXTENSION_CONF = 'default_extension.conf'


global extension_dict


def update_config(path=None):
    global extension_dict
    path = path or os.path.join(BASE_DIR, DEFAULT_EXTENSION_CONF)
    if os.path.exists(path):
        conf = ConfigParser()
        conf.read(path)
        for section in conf.sections():
        	extension_dict.update(conf._sections[section])


def filetype(filename=None):
    if filename is None:
        return None
    update_config()
    basename, ext = os.path.splitext(filename)
    if ext in extension_dict:
        return extension_dict[ext]
    format = ase.io.formats.filetype(filename, read=os.path.exists(filename))
    # print(filename, format)
    if format in extension_dict:
        format = extension_dict[format]
    return format


update_config()


