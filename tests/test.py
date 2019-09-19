"""


test


"""



import os
import gaseio
from gaseio import gase_writer
import tempfile
import json_tricks

BASEDIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASEDIR, 'chem_file_samples/files')
SUPPORTED_TEMPS = gase_writer.list_supported_write_formats()
print('SUPPORTED_TEMPS', SUPPORTED_TEMPS)


print(gaseio)
print(gaseio.__version__)


CONTINUE_FILE = os.environ.get("GASEIO_CONTINUE_FILE", None)
CONTINUE_START_ITEM = 0
if CONTINUE_FILE:
    print("CONTINUE_FILE", CONTINUE_FILE)
    if os.path.exists(CONTINUE_FILE):
        CONTINUE_START_ITEM = int(open(CONTINUE_FILE).read().strip())


def test_basic():
    return gaseio.version()


def test(test_types=None):
    
    for filename in os.listdir(TEST_DIR)[CONTINUE_START_ITEM:]:
        filename = os.path.join(TEST_DIR, filename)
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
                print(json_tricks.dumps(arrays)[1000])
    return error


def test_no_catch():
    """
    test gaseio without catching errors
    """
    for item_i, filename in enumerate(os.listdir(TEST_DIR)[CONTINUE_START_ITEM:]):
        print(filename)
        filename = os.path.join(TEST_DIR, filename)
        if not os.path.isfile(filename):
            continue
        print('\n'*4, filename)
        arrays = gaseio.read(filename, index=-1, force_gase=True)
        # print(arrays)
        print('\n' * 4)
        if not 'symbols' in arrays:
            continue
        for write_temp_type in SUPPORTED_TEMPS:
            print('\n'*4, )
            print(write_temp_type, filename)
            tmpfname = tempfile.mktemp()
            gaseio.write(tmpfname, arrays, write_temp_type, force_gase=True, preview=True)
        arrays = gaseio.read(filename, index=':', force_gase=True)
        open(CONTINUE_FILE, 'w').write(str(item_i+CONTINUE_START_ITEM))
        # print(arrays)
        print('\n' * 4)
    os.remove(CONTINUE_FILE)

if __name__ == '__main__':
    test_no_catch()
