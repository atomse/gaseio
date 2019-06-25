"""
Test gase.io
"""



import os
import gase.io


BASEDIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASEDIR, 'Testcases')
TEMPLATES_DIR = os.path.join(BASEDIR, '../gaseio/input_templates/')




def test(test_types=None):
    
    for filename in os.listdir(TEST_DIR):
        filename = os.path.join(TEST_DIR, filename)
        if filename.startswith('.') or not os.path.isfile(filename):
            continue
        print('\n'*4, filename)
        try:
            atoms = gase.io.read(filename, force_gase=True)
        except Exception as e:
            print(e)
            error = 1
            continue
        for filetype in os.listdir(TEMPLATES_DIR):
            try:
                gase.io.write('/tmp/test', atoms, filetype, force_gase=True, preview=True)
            except Exception as e:
                print(filetype, 'tempelate wrong!', filename)
                print(e)
                print(atoms)
    return error


def test_no_catch():
    """
    test gase.io without catching errors
    """
    all_atoms = {}
    for filename in os.listdir(TEST_DIR):
        print(filename)
        if filename.startswith('.'):
            continue
        filename = os.path.join(TEST_DIR, filename)
        if not os.path.isfile(filename):
            continue
        print('\n'*4, filename)
        atoms = gase.io.read(filename)#force_gase=True, )
        # atoms = gase.io.read(filename, force_gase=True, )
        print(atoms)
        print('\n' * 4)
        # for filetype in os.listdir(TEMPLATES_DIR):
        #     print('\n'*4, )
        #     print(filetype, filename)
        #     gase.io.write('/tmp/test', atoms, filetype, force_gase=True, preview=True)
        all_atoms[os.path.basename(os.path.splitext(filename)[0])] = atoms
    return all_atoms


if __name__ == '__main__':
    test_no_catch()
