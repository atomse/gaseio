"""
analyze filetype 
"""


import os
import re
import configparser
import atomtools


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILETYPE_REGEXP_CONF = 'default_extension.conf'
USER_FILETYPE_REGEXP_CONF = os.path.expanduser('~/.gase/user_extension.conf')
REG_ANYSTRING = '[\s\S]*?'

global format_regexp
format_regexp = dict()


def update_config(path=None):
    global format_regexp
    path = path or os.path.join(BASE_DIR, DEFAULT_FILETYPE_REGEXP_CONF)
    if os.path.exists(path):
        conf = configparser.ConfigParser()
        conf.optionxform=str
        conf.read(path)
        for section in conf.sections():
            format_regexp.update(conf._sections[section])


def filetype(fileobj=None, isfilename=False, debug=False):
    """
    >>> filetype("a.gjf")
    gaussian
    """
    if isfilename:
        filename = fileobj
    else:
        filename = atomtools.file.get_filename(fileobj)
    content = atomtools.file.get_file_content(fileobj)
    if filename is None and content is None:
        return None
    for fmt_regexp, fmt_filetype in format_regexp.items():
        name_regexp, content_regexp = (fmt_regexp.split('||') + [None])[:2]
        if debug:
            print(name_regexp)
        if filename and re.match(re.compile(name_regexp.strip()), filename) or filename is None:
            if content and content_regexp:
                content_regexp = REG_ANYSTRING + content_regexp.strip() + REG_ANYSTRING
                if debug:
                    print(content_regexp)
                    import pdb; pdb.set_trace()
                if re.match(re.compile(content_regexp.strip()), content):
                    return fmt_filetype
            else:
                return fmt_filetype
    return None

def create_user_regexp():
    if not os.path.exists(USER_FILETYPE_REGEXP_CONF):
        if not os.path.exists(os.path.dirname(USER_FILETYPE_REGEXP_CONF)):
            os.makedirs(os.path.dirname(USER_FILETYPE_REGEXP_CONF))
        with open(USER_FILETYPE_REGEXP_CONF, 'w') as fd:
            fd.write('[user]\n')


update_config()
create_user_regexp()
update_config(USER_FILETYPE_REGEXP_CONF)



