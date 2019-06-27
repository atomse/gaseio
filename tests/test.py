



import os
import gaseio


BASEDIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASEDIR, 'Testcases')
TEMPLATES_DIR = os.path.join(BASEDIR, '../gaseio/input_templates/')


def test_basic():
    return gaseio.version()


def test(test_types=None):
    
    for filename in os.listdir(TEST_DIR):
        filename = os.path.join(TEST_DIR, filename)
        if filename.startswith('.') or not os.path.isfile(filename):
            continue
        print('\n'*4, filename)
        try:
            arrays = gaseio.read(filename, force_gase=True)
        except Exception as e:
            print(e)
            error = 1
            continue
        for filetype in os.listdir(TEMPLATES_DIR):
            try:
                gaseio.write('/tmp/test', arrays, filetype, force_gase=True, preview=True)
            except Exception as e:
                print(filetype, 'tempelate wrong!', filename)
                print(e)
                print(arrays)
    return error


def test_no_catch():
    """
    test gaseio without catching errors
    """
    for filename in os.listdir(TEST_DIR):
        print(filename)
        if filename.startswith('.'):
            continue
        filename = os.path.join(TEST_DIR, filename)
        if not os.path.isfile(filename):
            continue
        print('\n'*4, filename)
        arrays = gaseio.read(filename, index=-1, force_gase=True)
        print(arrays)
        print('\n' * 4)
        for filetype in os.listdir(TEMPLATES_DIR):
            print('\n'*4, )
            print(filetype, filename)
            gaseio.write('/tmp/test', arrays, filetype, force_gase=True, preview=True)
        arrays = gaseio.read(filename, index=':', force_gase=True)
        print(arrays)
        print('\n' * 4)

if __name__ == '__main__':
    test_no_catch()
