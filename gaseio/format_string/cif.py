"""
format_string
"""


def parse_cif(data, index):
    import os
    import tempfile
    import ase.io
    tmpfname = tempfile.mktemp(suffix='.cif')
    with open(tmpfname, 'w') as fd:
        fd.write(data)
    arrays = list()
    try:
        atoms = ase.io.read(tmpfname, index=index, format='cif')
        isAtoms = False
        if isinstance(atoms, ase.Atoms):
            atoms = [atoms]
            isAtoms = True
        for x in atoms:
            arr = x.arrays
            arr.update({
                'cell': x.cell.array,
                'pbc': x.pbc,
                'cell_disp': x.get_celldisp(),
                'info' : x.info,
            })
            if 'spacegroup' in x.info:
                arr['info'].update({
                    'spacegroup': x.info['spacegroup'].__dict__,
                })
            arrays.append(arr)
        if isAtoms:
            arrays = arrays[0]
    finally:
        os.remove(tmpfname)
    return arr


FORMAT_STRING = {
    'cif': {
        'parser_type': 'customized',
        'parser': parse_cif,
        # 'multiframe': True,
        # 'frame_spliter': r'\n',
    },
}
