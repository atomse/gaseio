# -*- coding: utf-8 -*-

import os
import re
import hashlib
import logging
from werkzeug.utils import secure_filename
from flask import Flask, request, send_from_directory
from flask_compress import Compress


import json_tricks

import atomtools.name
import gaseio


UPLOAD_DIR = os.environ.get(
    "GASEIO_UPLOAD_DIR", os.path.expanduser('~/chemio'))
if not os.path.exists(UPLOAD_DIR):
    raise IOError(UPLOAD_DIR, 'not exist')


app = Flask(__name__, static_url_path='/static')
BASEDIR = os.path.dirname(os.path.realpath(__file__))
HTMLDIR = os.path.join(BASEDIR, 'html')

Compress(app)


def return_msg(code, msg):
    return {
        'code': code,
        'msg': msg,
    }


def allowed_file(filename):
    return True


def parse_data(data):
    data_array = dict()
    for d in data.split(';'):
        match = re.match('^(.*?)=(.*)$', d)
        if match:
            key, val = match[1], match[2]
            data_array[key] = val
    return data_array


def read_from_request(inp_request):
    "read_from_request"
    upload_file = inp_request.files['read_file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        # 将文件保存到 static/uploads 目录，文件名同上传时使用的文件名
        # dest_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        dest_filename = os.path.join(
            UPLOAD_DIR,
            atomtools.name.randString() + '_' + filename)
        upload_file.save(dest_filename)
    else:
        return return_msg(200, 'file not allow to upload')
    form = inp_request.form
    format = form.get('read_formats', None)
    filename = form.get('read_filename', filename)
    index = form.get('read_index', None)
    data_array = parse_data(form.get('data', ''))
    data_calc_array = parse_data(form.get('calc_data', ''))
    logging.debug(f"filename: {filename}")
    logging.debug(f"data_array: {data_array}")
    logging.debug(f"data_calc_array: {data_calc_array}")
    if index == 'on':
        index = ':'
    elif index == 'off' or index is None:
        index = -1
    arrays = gaseio.read(dest_filename, index, format, force_gase=True)
    if isinstance(arrays, dict):
        arrays['filename'] = filename
        arrays.update(data_array)
        if not 'calc_arrays' in arrays:
            arrays['calc_arrays'] = dict()
        arrays['calc_arrays'].update(data_calc_array)
        gaseio.regularize.regularize_arrays(arrays)
    elif isinstance(arrays, list):
        for arr in arrays:
            arr['filename'] = filename
            arr.update(data_array)
            if not 'calc_arrays' in arr:
                arr['calc_arrays'] = dict()
            arr['calc_arrays'].update(data_calc_array)
            gaseio.regularize.regularize_arrays(arr)
    logging.debug(f"filename: {filename}")
    logging.debug(f"arrays: {arrays}")
    logging.debug(json_tricks.dumps(arrays, indent=4))
    return arrays


@app.route('/read', methods=['POST'])
def app_read():
    "app_read"
    arrays = read_from_request(request)
    return json_tricks.dumps(arrays)


def write_with_request(inp_request, arrays):
    "write_with_request"
    form = inp_request.form
    filename = form.get('write_filename', None)
    fileformat = form.get('write_format', None)
    logging.debug(f"{form}\n{filename}\n{fileformat}")
    if not filename and not fileformat:
        msg = 'filename and format cannot be None at the same time'
        if app.debug:
            raise ValueError(msg)
        return {'success': False, 'msg': msg}
    if filename:
        if isinstance(arrays, dict):
            arrays['filename'] = filename
        elif isinstance(arrays, list):
            for arr in arrays:
                arr['filename'] = filename
    logging.debug(f"filename: {filename}")
    output = gaseio.get_write_content(
        filename, arrays, fileformat, force_gase=True)
    return output


@app.route('/write', methods=['POST'])
def app_write():
    "app_write"
    form = request.form
    arrays_string = form.get('arrays', None)
    arrays = json_tricks.loads(arrays_string)
    return write_with_request(request, arrays)


@app.route('/convert', methods=['POST'])
def app_convert():
    "app_convert"
    arrays = read_from_request(request)
    output = write_with_request(request, arrays)
    return output


if __name__ == '__main__':
    DEFAULT_GASEIO_PORT = 5000 + 1
    port = os.environ.get("GASEIO_PORT", DEFAULT_GASEIO_PORT)
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=port, debug=True)
