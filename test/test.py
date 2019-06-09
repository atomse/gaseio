



import os
import gaseio
print(gaseio)



BASEDIR = os.path.dirname(os.path.abspath(__file__))


def test(test_types=None):
    test_dir = os.path.join(BASEDIR, 'testcases')
    for filename in os.listdir(test_dir):
        if filename.startswith('.'):
            continue
        filename = os.path.join(test_dir, filename)
        print(filename)
        if os.path.isfile(filename):
            print(gaseio.read(filename, force_fmt=True, debug=True))




if __name__ == '__main__':
    test()
