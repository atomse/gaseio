"""



generate a .ini/.conf file for supervisord


"""


import os
import sys
import jinja2

rootdir = os.path.dirname(os.path.dirname(sys.executable))
basedir = os.path.dirname(os.path.abspath(__file__))

INPUT_TEMPLATE_DIR = os.path.join(basedir, 'supervisord_templates')

jinja_loader = jinja2.FileSystemLoader(INPUT_TEMPLATE_DIR)
jinja_environment = jinja2.Environment(loader=jinja_loader, lstrip_blocks=True)


def get_dirname_suffix():
    import configparser
    for supervisord_conf in ['/etc/supervisord.conf', '/etc/supervisor/supervisord.conf']:
        if os.path.exists(supervisord_conf):
            break
    if not os.path.exists(supervisord_conf):
        raise NotImplementedError("supervisord not installed")
    conf = configparser.ConfigParser()
    conf.read(supervisord_conf)
    files_option = conf.get("include", "files")
    dirname, suffix = os.path.splitext(files_option)
    dirname = os.path.dirname(dirname)
    dirname = os.path.join(os.path.dirname(supervisord_conf), dirname)
    return dirname, suffix


def generate_supervisord_conf():
    dirname, suffix = get_dirname_suffix()
    fname = f"gaseio{suffix}"
    template = jinja_environment.get_template("gaseio.j2")
    output = template.render(rootdir=rootdir)
    dest_fname = f"/tmp/{fname}"
    with open(dest_fname, 'w') as fd:
        fd.write(output)
    return dest_fname, dirname


def main():
    src_fname, dest_dir = generate_supervisord_conf()
    print(f"please copy {src_fname} to {dest_dir}")
    print(f"cp {src_fname} {dest_dir}")


if __name__ == "__main__":
    main()
