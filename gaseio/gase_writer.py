"""
using jinja2 to generate input files.
Templates are stored in INPUT_TEMPLATE_DIR
"""



import os
import glob
import jinja2
import json_tricks
import atomtools
import basis_set_exchange as bse

from . import ext_types
from .regularize import regularize_arrays


BASEDIR = os.path.dirname(os.path.abspath(__file__))
INPUT_TEMPLATE_DIR = 'input_templates'
INPUT_TEMPLATE_DIR = os.path.join(BASEDIR, INPUT_TEMPLATE_DIR)

def islist(value):
    return isinstance(value, list)

def file_basename(value):
    return os.path.splitext(value)[0]


jinja_loader = jinja2.FileSystemLoader(INPUT_TEMPLATE_DIR)
jinja_environment = jinja2.Environment(loader=jinja_loader, lstrip_blocks=True)
jinja_environment.trim_blocks = True
jinja_environment.filters.update({
    'islist': islist,
    'file_basename' : file_basename,
})
jinja_environment.globals.update(get_basis=bse.get_basis, get_all_basis_names=bse.get_all_basis_names)

# def include_vasppot(fname):
#     print(fname)
#     potpaw_PBE_dir = 'potpaw_PBE'
#     fname = os.path.join(BASEDIR, potpaw_PBE_dir, str(fname), 'POTCAR')
#     _tmp = jinja_loader.get_source(jinja_environment, fname)[0]
#     print(_tmp)
#     return jinja2.Markup(_tmp)
# 
# 
# jinja_environment.globals['include_vasppot'] = include_vasppot


def generate_input_content(arrays, filetype):
    template_name = filetype + '.j2'
    template = jinja_environment.get_template(template_name)
    if not isinstance(arrays, dict) and hasattr(arrays, 'get_positions'):
        module_name = arrays.__class__.__module__
        if module_name == 'ase.atoms':
            atoms = arrays
            calc = atoms.calc
            arrays = atoms.arrays.copy()
            arrays['symbols'] = ext_types.ExtList(atoms.get_chemical_symbols())
            if calc is not None:
                arrays['calc_arrays'] = {}
                arrays['calc_arrays'].update(calc.parameters)
                arrays['calc_arrays'].update(calc.results)
        # if module_name == 'ase.atoms':
        else: # gase
            arrays = arrays.arrays
    regularize_arrays(arrays)
    # print(arrays['symbols'])
    if isinstance(arrays, list):
        output = template.render(arrays=arrays, arrays_json=json_tricks.dumps(arrays),
                                 randString=atomtools.name.randString())
    else:
        output = template.render(arrays=arrays, arrays_json=json_tricks.dumps(arrays),
                                 randString=atomtools.name.randString(), **arrays)
    return output


def preview(arrays, filetype):
    print('\n\n\n-------preview start from here------')
    print(generate_input_content(arrays, filetype))


def generate_inputfile(arrays, filetype, inputfilename):
    output = generate_input_content(arrays, filetype)
    with open(inputfilename, 'w') as fd:
        fd.write(output)


def list_supported_write_formats():
    return [os.path.splitext(os.path.basename(_))[0] \
        for _ in glob.glob(os.path.join(INPUT_TEMPLATE_DIR, '*.j2'))]

