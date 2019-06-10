"""
using jinja2 to generate input files.
Templates are stored in INPUT_TEMPLATE_DIR
"""



import os
import jinja2

BASEDIR = os.path.dirname(os.path.abspath(__file__))
INPUT_TEMPLATE_DIR = 'input_templates'

jinja_temp_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(BASEDIR, INPUT_TEMPLATE_DIR)))



def generate_input_content(arrays, filetype):
    jinja_temp_env.trim_blocks = True
    template = jinja_temp_env.get_template(filetype)
    output = template.render(**arrays)
    return output


def preview(arrays, filetype):
    print('\n\n\n-------preview start from here------')
    print(generate_input_content(arrays, filetype))


def generate_inputfile(arrays, filetype, inputfilename):
    output = generate_input_content(arrays, filetype)
    with open(inputfilename, 'w') as fd:
        fd.write(output)


if __name__ == '__main__':
    import os, glob
    # os.chdir('/tmp')
    test_cases = [
        {
            'filetype' : 'gaussian',
            'program_cmd' : 'vasp',
            'pbs_processPerNode' : 8,
        },
        {
            'program_cmd' : 'g09',
            'program_args' : 'ch4.gjf',
            'pbs_processPerNode' : 4,
        },
        {
            'env_files' : ['/home/scicons/openmpi/openmpi.sh'],
            'program_cmd' : 'orca', 'program_args' : 'orca.inp',
        },
        {
            'program_cmd' : 'gmx',
            'program_args' : 'mdrun -f 1.gro',
        },
    ]

    for case in test_cases:
        print(pbs_jinja(**case))
        generate_pbs_subfile(**case)

    for file in glob.glob('*.sub'):
        os.system('cat {0}'.format(file))