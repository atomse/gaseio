"""
GASEIO
"""


__version__ = '2.4.5'
def version():
    return __version__

from .main import read, write
from .main import read_preview, write_preview, preview, get_write_content
from .main import list_supported_write_formats
