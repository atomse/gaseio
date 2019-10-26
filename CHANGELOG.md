# CHANGELOG

## 2.7.3


* add multi-processing support


## 2.7.0


* refactor structure to standard and customized
* using ASE cif parser
* fix gaussian-log bugs
* add json support


## 2.6.9 

* fix INCAR TPAR/KPAR/NPAR, set default LCHARG=.True. 
* add cessp test
* fix app bugs

## 2.6.8

* fix POTCAR bug


## 2.6.7

* adjust Gaussian forces


## 2.6.6

* add kinetic_energy


## 2.6.5

* autopep8 all .py code
* ExtList used only in jinja2 files for numbers and symbols contraction

## 2.6.4

* compatible with ASE, including
    - Atoms: cell, pbc, masses, constraints, chemical_formula, ...
    - Calculator: name, get_property, ...
* json acceptable


## 2.6.2

* `json_tricks` allow NaN
## 2.6.1

* Gaussian MO Coefficient fix
* fix app bug

## 2.6.0

* reset logging as log output


## 2.5.9

* `max_core`, `max_memory`
* supporting `data`/`calc_data`


## 2.5.8 

* fix adf bug



## 2.5.7

* rm bigfiles out to qcdata


## 2.5.6

* gromacs cell min 21Ang.

## 2.5.5

* update atomtools to make it faster & no misunderstanding



## 2.5.4

### functions

* add mod iolist to list supported parse/gen formats
* improve atomtools to speed up.
* update requirements

### fix

* gaussian-nbo-out lower_diagnal_order_2_square




## 2.5.3

### improve

* flask app compress
* adjust port with environment `GASEIO_PORT`, default 5000
* interface: read/write/convert
* update chem_file_samples






## 2.5.2

### improve

* gaussian-neb-out key: case unchangd, space-->underlinet


## 2.5.1

### fix

* pdb chemio read error
* gaussian-nbo-out .49 parse




## 2.5.0

### functions

* pdb supported, HETATM in arrays['hetatoms']
* add pdb test case
* using ext_methods.datablock_to_numpy_fixed_width to parse fix width format
* using datablock_to_numpy_fixed_width parse gromacs and pdb



## 2.4.9

### functions

* gaussian input 输出 basis, ecp, connectivity部分
* requirements.txt 添加 basis_set_exchange




## 2.4.8

### functions

* VASP INCAR 完整解析

### adjusts

* maxmem --> max_memory



## 2.4.7

### functions

* 拆分update 和 deploy, 初次运行`deploy.sh`，升级使用`update.sh`

### fix

* requirements.txt 缺少 Tornado





## 2.4.6

### functions

* version模块
* VASP 默认 INCAR




## 2.4.5

### functions

* 使用Tornado部署，调整原有server.py-->app.py，Tornado部分为server.py



## 2.4.4

### functions

* 使用Flask网络服务

### adjusts

* requirements

### fix

* gaseio.py-->main.py,防止server.py导入gaseio包出错
* maxcore 强制整数





## 2.4.3


### functions

* 测试发生错误，再次测试可以从最近的失败位置继续
* 解析时加入arrays['filename']
* 增加gaussian-out的maxcore、maxmem解析
* 增加CP2K若干项解析
* jinja2模板渲染增加randString


### adjusts

* 输出文件状态atomtools.Status调整为error、complete、unfinished三项
* 调整maxcore、maxmem至calc_arrays下
* write函数调整为ase_writer与gase_writer，类似read函数


### fix

* `.gitignore`忽略测试样例，并加入样例
* write时positions可能给出科学计数法的错误
* ext_methods.datablock_to_numpy可能出现的错误，将pandas长度最大化变为datablock_to_numpy_extend
* gaussian genecp解析可能出现的**-元素**的错误，如'-C -P 0'
* gaussian ECP解析分割器修复
* list_supported_write_formats输出列表


## 2.4.2

### functions
* abinit解析
* gaussian的genecp、connectivity部分的解析
* gaussian-fchk的解析
* arrays正则化添加atoms_size
* write模板min_cell_size、atoms_size参数

### adjusts

* VASP POT升级至5.4.4


### fix

* gaussian charge、multiplicity、appendix、genecp的正则解析可能出错




## 2.0.0

### functions

使用jinja2 模板进行输出






## ...


## 1.0.0

### functions

使用python正则表达式进行解析



<!-- 

## 

### functions

### adjusts

### fix

 -->
