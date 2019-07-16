"""
format_string
"""
from collections import OrderedDict
import numpy as np
import parse

from .. import ext_methods


"""
http://www.wwpdb.org/documentation/file-format-content/format33/sect9.html#ATOM

https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/tutorials/pdbintro.html

ITEM  COLUMNS            DATA  TYPE    FIELD        DEFINITION
-------------------------------------------------------------------------------------
0      1 -  6    6  x    Record name   "ATOM  "
1      7 - 11    5  x    Integer       serial       Atom  serial number.
2     12 - 12    1  x    space * 1
3     13 - 16    4  s    Atom          name         Atom name.
4     17 - 18    1  s    Character     altLoc       Alternate location indicator.
5     18 - 20    3  d    Residue name  resName      Residue name.
6     21 - 21    1  x    space * 1
7     22 - 23    1  s    Character     chainID      Chain identifier.
8     23 - 26    4  d    Integer       resSeq       Residue sequence number.
9     27 - 27    1  s    AChar         iCode        Code for insertion of residues.
10    28 - 30    3  x    space * 3
11    31 - 38    8  f    Real(8.3)     x            Orthogonal coordinates for X in Angstroms.
12    39 - 46    8  f    Real(8.3)     y            Orthogonal coordinates for Y in Angstroms.
13    47 - 54    8  f    Real(8.3)     z            Orthogonal coordinates for Z in Angstroms.
14    55 - 60    6  f    Real(6.2)     occupancy    Occupancy.
15    61 - 66    6  f    Real(6.2)     tempFactor   Temperature  factor.
16    67 - 76    10 x    space * 10
17    77 - 78    2  s    LString(2)    element      Element symbol, right-justified.
18    79 - 80    2  s    LString(2)    charge       Charge  on the atom.


00000000011111111112222222222333333333344444444445555555555666666666677777777778
12345678901234567890123456789012345678901234567890123456789012345678901234567890
ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C



python test

import parse
PDB_ATOM_FORMAT_STRING = "ATOM  {:5d} {:4} {:3} {:1}{:4d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:2S}{:2}"
string = 'ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C  '
parse.parse(PDB_ATOM_FORMAT_STRING, string)



import struct
import sys

# fieldwidths = (2, -10, 24)  # negative widths represent ignored padding fields
# fieldformats = ('s', '')
# fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
#                         for fw in fieldwidths)

# fieldstruct = struct.Struct(fmtstring)
# if sys.version_info[0] < 3:
#     parse = fieldstruct.unpack_from
# else:
#     # converts unicode input to byte string and results back to unicode string
#     unpack = fieldstruct.unpack_from
#     parse = lambda line: tuple(s.decode() for s in unpack(line.encode()))

# print('fmtstring: {!r}, recsize: {} chars'.format(fmtstring, fieldstruct.size))

# line = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n'
# fields = parse(line)
# print('fields: {}'.format(fields))

# format: '2s 10x 24s', rec size: 36 chars
# fields: ('AB', 'MNOPQRSTUVWXYZ0123456789')


--------------------------------------------------------------------------------
# v1

import struct
import sys

fieldwidths = ( -6,-5,-1,4 ,1 ,3 ,-1,1 ,4 ,1 ,-3,8 ,8 ,8 ,6 ,6 ,-1,2 ,2 )
fieldformts = ("x", "x", "x", "s", "s", "d", "x", "s", "d", "s", "x", "f", "f", "f", "f", "f", "x", "s", "s")
fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
                        for fw in fieldwidths)

fieldstruct = struct.Struct(fmtstring)
if sys.version_info[0] < 3:
    parse = fieldstruct.unpack_from
else:
    # converts unicode input to byte string and results back to unicode string
    unpack = fieldstruct.unpack_from
    parse = lambda line: tuple(s.decode() for s in unpack(line.encode()))

print('fmtstring: {!r}, recsize: {} chars'.format(fmtstring, fieldstruct.size))

line = 'ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C  '
fields = parse(line)
print('fields: {}'.format(fields))



--------------------------------------------------------------------------------
# v2

import struct
import sys

fieldwidths = ( -6,-5,-1,4 ,1 ,3 ,-1,1 ,4 ,1 ,-3,8 ,8 ,8 ,6 ,6 ,-1,2 ,2 )
fieldformts = ("x", "x", "x", "s", "s", "i", "x", "s", "i", "s", "x", "s", "s", "s", "s", "s", "x", "s", "s")
fmtstring = ' '.join('{}{}'.format(abs(fw), ff)
                        for fw,ff in zip(fieldwidths, fieldformts))

fieldstruct = struct.Struct(fmtstring)
if sys.version_info[0] < 3:
    parse = fieldstruct.unpack_from
else:
    # converts unicode input to byte string and results back to unicode string
    unpack = fieldstruct.unpack_from
    parse = lambda line: tuple(s.decode() for s in unpack(line.encode()))

print('fmtstring: {!r}, recsize: {} chars'.format(fmtstring, fieldstruct.size))

line = 'ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C  '
fields = parse(line)
print('fields: {}'.format(fields))


--------------------------------------------------------------------------------
# pack

import struct
import sys

fieldwidths = ("6","5","1","4","1","3","1","1","4","1","3","8.3","8.3","8.3","6.2","6.2","10","2","2")
fieldformts = ("x","x","x","s","s","d","x","s","d","s","x","f","f","f","f","f","x","s","s")
data = ('ATOM', 4893, ' ', 'CE1', ' ', 'TYR', ' ', 'A', 664, ' ', '   ', 38.747, 66.914, 36.840, 1.00, 38.37, '          ', 'C', '  ')
line = 'ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C  '
print(len(fieldwidths), len(fieldformts))
fmtstring = ''.join('{}{}'.format(fw, ff)
                        for fw,ff in zip(fieldwidths, fieldformts))

fieldstruct = struct.Struct(fmtstring)
# if sys.version_info[0] < 3:
#     parse = fieldstruct.pack_from
# else:
#     # converts unicode input to byte string and results back to unicode string
#     unpack = fieldstruct.pack_from
#     parse = lambda line: tuple(s.decode() for s in unpack(line.encode()))

print('fmtstring: {!r}, recsize: {} chars'.format(fmtstring, fieldstruct.size))

print(fieldstruct.pack(*data))
print(line)


--------------------------------------------------------------------------------
# pandas

import pandas as pd
from io import StringIO

line = 'ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C  '
PDB_COL_SPECIFICATION = [[1 ,  6], [7 , 11],[12 , 12],[13 , 16],[17 , 18],[18 , 20],[21 , 21],[22 , 23],[23 , 26],[27 , 27],[28 , 30],[31 , 38],[39 , 46],[47 , 54],[55 , 60],[61 , 66],[67 , 76],[77 , 78],[79 , 80]]
PDB_COL_SPECIFICATION = [[i-1, j] for i, j in PDB_COL_SPECIFICATION]

data = pd.read_fwf(StringIO(line), colspecs=PDB_COL_SPECIFICATION, header=None)


print(data.values.flatten().tolist())



data = 'ATOM   4893  CE1 TYR A 664      38.747  66.914  36.840  1.00 38.37           C  '
PDB_COL_SPECIFICATION = [[1 ,  6], [7 , 11],[12 , 12],[13 , 16],[17 , 18],[18 , 20],[21 , 21],[22 , 23],[23 , 26],[27 , 27],[28 , 30],[31 , 38],[39 , 46],[47 , 54],[55 , 60],[61 , 66],[67 , 76],[77 , 78],[79 , 80]]
PDB_COL_SPECIFICATION = [[i-1, j] for i, j in PDB_COL_SPECIFICATION]

data = pd.read_fwf(StringIO(data), colspecs=PDB_COL_SPECIFICATION, header=None).values
print(data)


"""


PDB_ATOM_FORMAT_STRING = "ATOM  {:5d} {:4} {:3} {:1}{:4d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:2S}{:2}"
PDB_COL_SPECIFICATION = [[1 ,  6], [7 , 11],[12 , 12],[13 , 16],[17 , 17],[18 , 20],[21 , 21],[22 , 22],[23 , 26],[27 , 27],[28 , 30],[31 , 38],[39 , 46],[47 , 54],[55 , 60],[61 , 66],[67 , 76],[77 , 78],[79 , 80]]
PDB_COL_SPECIFICATION = [(i-1, j) for (i, j )in PDB_COL_SPECIFICATION]

FORMAT_STRING = {
    'pdb': {
        'primitive_data'  : OrderedDict({
            # r'':{
            #     'important': True,
            #     'selection' : -1,
            #     'key' : 'comments',
            #     'type' : str,
            # },
            r'\n(ATOM[\s\S]*?)\n(?!ATOM)':{
                # 'debug' : True,
                'important': True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy_fixed_width(data, colspecs=PDB_COL_SPECIFICATION, nan_fill=''),
                'key' : [
                    {
                        "key" :    "customized_symbols",
                        "index" : ":,3",
                        'type' : str,
                        'process' : lambda data, arrays: [_.strip() for _ in data],
                    },
                    {
                        "key" :    "altLoc",
                        "index" : ":,4",
                        # 'type' : str,
                    },
                    {
                        "key" :    "residue_name",
                        "index" : ":,5",
                        'type' : str,
                    },
                    {
                        "key" :    "chainID",
                        "index" : ":,7",
                        'type' : str,
                    },
                    {
                        "key" :    "resSeq",
                        "index" : ":,8",
                        'type' : int,
                    },
                    {
                        "key" :    "iCode",
                        "index" : ":,9",
                        'type' : str,
                    },
                    {
                        "key" :   "positions",
                        "index" : ":,11:14",
                        'type' : float,
                    },
                    {
                        "key" :   "occupancy",
                        "index" : ":,14",
                        'type' : float,
                    },
                    {
                        "key" :   "temperature_factor",
                        "index" : ":,15",
                        'type' : float,
                    },
                    {
                        "key" :   "symbols",
                        "index" : ":,17",
                        'type' : str,
                        'process' : lambda data, arrays: data.tolist(),
                    },
                    {
                        "key" :   "pdb_charge",
                        "index" : ":,18",
                        'type' : str,
                    },
                ],
            },
            r'\n(HETATM[\s\S]*?)\n(?!HETATM)':{
                'important': True,
                'selection' : -1,
                'process' : lambda data, arrays: ext_methods.datablock_to_numpy_fixed_width(data, \
                                                 colspecs=PDB_COL_SPECIFICATION),
                'key' : [
                    {
                        "key" :    "hetatoms/customized_symbols",
                        "index" : ":,3",
                        'type' : str,
                        'process' : lambda data, arrays: [_.strip() for _ in data],
                    },
                    {
                        "key" :    "hetatoms/altLoc",
                        "index" : ":,4",
                        # 'type' : str,
                    },
                    {
                        "key" :    "hetatoms/residue_name",
                        "index" : ":,5",
                        'type' : str,
                    },
                    {
                        "key" :    "hetatoms/chainID",
                        "index" : ":,7",
                        'type' : str,
                    },
                    {
                        "key" :    "hetatoms/resSeq",
                        "index" : ":,8",
                        'type' : int,
                    },
                    {
                        "key" :    "hetatoms/iCode",
                        "index" : ":,9",
                        # 'type' : int,
                    },
                    {
                        "key" :   "hetatoms/positions",
                        "index" : ":,11:14",
                        'type' : float,
                    },
                    {
                        "key" :   "hetatoms/occupancy",
                        "index" : ":,14",
                        'type' : float,
                    },
                    {
                        "key" :   "hetatoms/temperature_factor",
                        "index" : ":,15",
                        'type' : float,
                    },
                    {
                        "key" :   "hetatoms/symbols",
                        "index" : ":,17",
                        'type' : str,
                        'process' : lambda data, arrays: data.tolist(),
                    },
                    {
                        "key" :   "hetatoms/pdb_charge",
                        "index" : ":,18",
                        #     'process' : lambda
                    },
                ],
            },
            # r'\d+\n.*\n([\s\S]*)':{
            #     'important': True,
            #     'selection' : 'all',
            #     'process' : lambda data, arrays: ext_methods.datablock_to_numpy(\
            #         data)[:,1:4].reshape((-1, arrays['natoms'], 3)),
            #     'key' : [
            #         {
            #             'key' : 'all_positions',
            #             'type' : float,
            #             'index' : ':,1:4,:'
            #         }
            #     ],
            # },
        }),
        'synthesized_data' : OrderedDict({
        }),
    },
}
