"""
GASEIO
"""


__version__ = '2.2.0'
def version():
    return __version__

from .gaseio import read, write, get_write_content, preview_write


