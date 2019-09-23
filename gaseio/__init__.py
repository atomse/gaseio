"""
GASEIO
"""


from .main import read, write
from .main import read_preview, write_preview, preview, get_write_content
from .main import list_supported_write_formats


__version__ = '2.6.2'

def version():
    return __version__
