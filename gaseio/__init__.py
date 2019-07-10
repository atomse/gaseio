"""
GASEIO
"""


__version__ = '2.4.2'
def version():
    return __version__

from .gaseio import read, write, read_preview, write_preview, preview, get_write_content
