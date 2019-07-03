"""
GASEIO
"""


__version__ = '2.3.0'
def version():
    return __version__

from .gaseio import read, write, read_preview, write_preview, preview


