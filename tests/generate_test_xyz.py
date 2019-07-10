"""


test xyz for all elements



"""




import chemdata
import gaseio


def main():
    arrays = {
        'symbols' : [],
        'positions' : [],
    }
    for i, ele in enumerate(chemdata.chemical_symbols[1:93]):
        arrays['symbols'].append(ele)
        arrays['positions'].append([i, i, i])
    gaseio.write('Testcases/test.xyz', arrays)


if __name__ == '__main__':
    main()