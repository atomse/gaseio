"""
Load all available format_string
"""

import os
import importlib
from collections import OrderedDict
from .. import format_parser
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

global FORMAT_STRING
FORMAT_STRING = OrderedDict()
def update_format_string(warning=False, DEBUG=False):
    global FORMAT_STRING
    mods = []
    for file in os.listdir(BASE_DIR):
        if file.endswith('.py') and not file.startswith('__'):
            basename, _ = os.path.splitext(file)
            mods.append(importlib.import_module('.'+basename,
                '{0}.format_string'.format('.'.join(format_parser.__name__.split('.')[:-1]))))
    
    for mod in mods:
        if DEBUG: import pdb; pdb.set_trace()
        if not hasattr(mod, 'FORMAT_STRING'):
            if warning: print('WARNING: {0} has not format_string'.format(mod.__name__))
            continue
        sub_format_string = getattr(mod, 'FORMAT_STRING')
        FORMAT_STRING.update(sub_format_string)
    return FORMAT_STRING


update_format_string()


def test():
    update_format_string(warning=True)
    print(FORMAT_STRING)
if __name__ == '__main__':
    test()
