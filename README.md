# GASEIO

Generalized Atomic Simulation Environment Input/Output

Split from GASE project



## Motivation

Using highly extensive code to read all kinds of chemical files, transform to a Atoms object.



## Core idea

Regular expression is the core to parse all files.




## Parse(Reverse format)

Python module [parse](https://github.com/r1chardj0n3s/parse) for Fix Format 



## Supported Formats

* xyz
* json
* gromacs/.gro [http://manual.gromacs.org/archive/5.0.3/online/gro.html]
* .gjf/.com gaussian input file
* .log/.out gaussian output file/adf output file/nwchem output file
* .top/.itp gromacs topology file
* .vasp/POSCAR/CONTCAR/ vasp POSITION file
* OUTCAR vasp OUTPUT file
* vasprun.xml vasprun xml file



