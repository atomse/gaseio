import os
import sys
import stat
import shutil
import time
from distutils.core import setup
from Cython.Build import cythonize

starttime = time.time()
CURDIR = os.path.abspath('.')
PARENTPATH = sys.argv[1] if len(sys.argv) > 1 else ""
setupfile = os.path.join(os.path.abspath('.'), __file__)
build_dir = "build"  # 项目加密后位置
build_tmp_dir = build_dir + "/temp"


NOT_COMPILED_FILES = ['setup.py', 'test.py']


def copy_complete(source, target):
    # copy content, stat-info (mode too), timestamps...
    shutil.copy2(source, target)
    # copy owner and group
    st = os.stat(source)
    os.chown(target, st[stat.ST_UID], st[stat.ST_GID])


def get_pythons(basepath=os.path.abspath('.'), parentpath='', name='',
                excepts=(), copyOther=False, delC=False):
    """
    获取py文件的路径
    :param basepath: 根路径
    :param parentpath: 父路径
    :param name: 文件/夹
    :param excepts: 排除文件
    :param copy: 是否copy其他文件
    :return: py文件的迭代器
    """
    fullpath = os.path.join(basepath, parentpath, name)
    # 返回指定的文件夹包含的文件或文件夹的名字的列表
    for fname in os.listdir(fullpath):
        ffile = os.path.join(fullpath, fname)
        print("ffile", ffile)
        # print basepath, parentpath, name,file
        # 是文件夹 且不以.开头 不是 build  ，不是迁移文件
        if os.path.isdir(ffile) and fname != build_dir and not fname.startswith('.') and fname != "migrations":
            print("fname", fname)
            for f in get_pythons(basepath, os.path.join(parentpath, name), fname, excepts, copyOther, delC):
                yield f
        elif os.path.isfile(ffile):
            ext = os.path.splitext(fname)[1]
            if ext == ".c":
                print("delC", delC)
                if delC and os.stat(ffile).st_mtime > starttime:
                    os.remove(ffile)
            elif ffile not in excepts and os.path.splitext(fname)[1] not in ('.pyc', '.pyx'):
                # manage.py文件不编译
                if os.path.splitext(fname)[1] in ('.py', '.pyx') and \
                        not fname.startswith('__') and \
                        not fname in NOT_COMPILED_FILES:
                    yield os.path.join(parentpath, name, fname)
                elif copyOther:
                    dstdir = os.path.join(
                        basepath, build_dir, parentpath, name)
                    if not os.path.isdir(dstdir):
                        os.makedirs(dstdir)
                    copy_complete(ffile, os.path.join(dstdir, fname))
        else:
            pass


def create_build_dir():
    if os.path.exists(build_dir):
        if os.path.isdir(build_dir):
            shutil.rmtree(build_dir)
        else:
            raise RuntimeError(
                f"build directory {build_dir} occupied by a file")


def encryption():
    # 获取py列表
    module_list = list(
        get_pythons(basepath=CURDIR, parentpath=PARENTPATH, excepts=(setupfile)))
    try:
        setup(ext_modules=cythonize(module_list), script_args=[
            "build_ext", "-b", build_dir, "-t", build_tmp_dir])
    except Exception as e:
        print(e)
    else:
        module_list = list(get_pythons(
            basepath=CURDIR, parentpath=PARENTPATH, excepts=(setupfile), copyOther=True))
    module_list = list(
        get_pythons(basepath=CURDIR, parentpath=PARENTPATH, excepts=(setupfile), delC=True))
    if os.path.exists(build_tmp_dir):
        shutil.rmtree(build_tmp_dir)
    print("complate! time:", time.time() - starttime, 's')


def main():
    create_build_dir()
    encryption()


if __name__ == '__main__':
    main()
