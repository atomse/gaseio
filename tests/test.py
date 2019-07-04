



import os
import gaseio
from gaseio import gase_writer

BASEDIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASEDIR, 'Testcases')
SUPPORTED_TEMPS = gase_writer.list_supported_write_formats()


print(gaseio)
print(gaseio.__version__)



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
        for write_temp_type in SUPPORTED_TEMPS:
            write_temp_type = write_temp_type.split('.')[0]
            try:
                gaseio.write('/tmp/test', arrays, write_temp_type, force_gase=True, preview=True)
            except Exception as e:
                print(write_temp_type, 'tempelate wrong!', filename)
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
        # print(arrays)
        print('\n' * 4)
        for write_temp_type in SUPPORTED_TEMPS:
            write_temp_type = os.path.basename(write_temp_type).split('.')[0]
            print('\n'*4, )
            print(write_temp_type, filename)
            gaseio.write('/tmp/test', arrays, write_temp_type, force_gase=True, preview=True)
        arrays = gaseio.read(filename, index=':', force_gase=True)
        # print(arrays)
        print('\n' * 4)

if __name__ == '__main__':
    test_no_catch()
