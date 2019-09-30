"""



list supported parsing types and gnerate types


"""

import os
import glob
import argparse


BASEDIR = os.path.dirname(os.path.abspath(__file__))
INPUT_TEMPLATE_DIR = 'input_templates'
INPUT_TEMPLATE_DIR = os.path.join(BASEDIR, INPUT_TEMPLATE_DIR)


def list_supported_parse_formats():
    from .format_string import FORMAT_STRING
    return list(FORMAT_STRING.keys())


def list_supported_gen_formats():
    return [os.path.splitext(os.path.basename(_))[0]
            for _ in glob.glob(os.path.join(INPUT_TEMPLATE_DIR, '*.j2'))]


def main():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('list_type', help='type parse/gen')
    args = parser.parse_args()
    if args.list_type.startswith('parse'):
        for x in list_supported_parse_formats():
            print('* {0}'.format(x))
    elif args.list_type.startswith('gen'):
        for x in list_supported_gen_formats():
            print('* {0}'.format(x))
    else:
        raise ValueError("Please give parse/gen(erate) as args")
