"""
Load all available format_string
"""

import os
import importlib
from collections import OrderedDict
import modlog

from .. import format_parser
from .. import ext_methods
from .__basic__ import BASIC_PRIMITIVE_DATA_FORMAT_STRING


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = modlog.getLogger(__name__)


def update_format_string():
    format_string = {}
    mods = []
    for fname in os.listdir(BASE_DIR):
        if (fname.endswith('.so') or fname.endswith('.py')) and \
                not (fname.startswith('__') or fname.startswith('XBASIC')):
            basename = fname.split('.')[0]
            mod_from = '.'+basename
            mod_name = '{0}.format_string'.format(
                '.'.join(format_parser.__name__.split('.')[:-1]))
            mods.append(importlib.import_module(mod_from, mod_name))
    logger.debug(f"mods: {mods}")
    for mod in mods:
        logger.debug(f'Updating format {mod}')
        if not hasattr(mod, 'FORMAT_STRING'):
            logger.warnings('WARNING: {0} has not format_string'.format(
                mod.__name__))
            continue
        sub_format_string = getattr(mod, 'FORMAT_STRING')
        for key, pattern in sub_format_string.items():
            if 'primitive_data' in pattern:
                pattern['primitive_data'].update(
                    BASIC_PRIMITIVE_DATA_FORMAT_STRING)
        format_string.update(sub_format_string)
    return format_string


FORMAT_STRING = update_format_string()
