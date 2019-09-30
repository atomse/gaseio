"""


basic format string


"""


BASIC_PRIMITIVE_DATA_FORMAT_STRING = {
    r'<filename>(.*)</filename>': {
        'selection': -1,
        'important': False,
        'key': 'file/origin_filename',
    },
    r'<hostname>(.*)</hostname>': {
        'selection': -1,
        'important': False,
        'key': 'file/origin_hostname',
    },
}
