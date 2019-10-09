"""
format_string
"""


def parse_json(data, index):
    import json_tricks
    return json_tricks.loads(data)


FORMAT_STRING = {
    'json': {
        'parser_type': 'customized',
        'parser': parse_json,
        'multiframe': True,
        'frame_spliter': r'\n',
    },
}
