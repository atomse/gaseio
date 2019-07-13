



from collections import Iterable



GROMACS_FORMAT_STRING = "{:5d}{:<5w}{:5w}{:5d}{:8.3f}{:8.3f}{:8.3f}{:8.4f}{:8.4f}{:8.4f}"
GROMACS_STRING = '    1DUM      U    1   0.051   0.017  -0.002  0.0000  0.0000  0.0000'

TESTS = {
    GROMACS_FORMAT_STRING : GROMACS_STRING,
    'PN-{:0>9d}' : 'PN-000000123',
    # "{:5d}{:5<w}{:5w}{:5d}" : '    1DUM      U    1',
}



import parse


def test():
    import pdb; pdb.set_trace()
    for f, s in TESTS.items():
        x = parse.parse(f, s)
        print(list(x))






if __name__ == '__main__':
    test()
