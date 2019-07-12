# CHANGELOG





## 2.4.3


### 功能

* 测试发生错误，再次测试可以从最近的失败位置继续
* 解析时加入arrays['filename']
* 增加gaussian-out的maxcore、maxmem解析
* 增加CP2K若干项解析
* jinja2模板渲染增加randString


### 调整

* 输出文件状态atomtools.Status调整为error、complete、unfinished三项
* 调整maxcore、maxmem至calc_arrays下
* write函数调整为ase_writer与gase_writer，类似read函数


### 修复

* `.gitignore`忽略测试样例，并加入样例
* write时positions可能给出科学计数法的错误
* ext_methods.datablock_to_numpy可能出现的错误，将pandas长度最大化变为datablock_to_numpy_extend
* gaussian genecp解析可能出现的**-元素**的错误，如'-C -P 0'
* gaussian ECP解析分割器修复
* list_supported_write_formats输出列表


## 2.4.2

### 功能
* abinit解析
* gaussian的genecp、connectivity部分的解析
* gaussian-fchk的解析
* arrays正则化添加atoms_size
* write模板min_cell_size、atoms_size参数

### 调整

* VASP POT升级至5.4.4


### 修复

* gaussian charge、multiplicity、appendix、genecp的正则解析可能出错




## 2.0.0

### 功能

使用jinja2 模板进行输出


### 调整

### 修复







## ...


## 1.0.0

### 功能

使用python正则表达式进行解析



<!-- 

## v

### 功能

### 调整

### 修复
 -->