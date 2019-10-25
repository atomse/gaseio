# -*- coding: utf-8 -*-

import os
# import re
# import hashlib
import logging
from werkzeug.utils import secure_filename
from flask import Flask
from flask import request
# from flask import send_from_directory
from flask import Response
from flask_compress import Compress

import json_tricks
import atomtools.name
import gaseio

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(__name__)


UPLOAD_DIR = os.environ.get(
    "GASEIO_UPLOAD_DIR", os.path.expanduser('~/chemio'))
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    # raise IOError(UPLOAD_DIR, 'not exist')


app = Flask(__name__, static_url_path='/static')
BASEDIR = os.path.dirname(os.path.realpath(__file__))
HTMLDIR = os.path.join(BASEDIR, 'html')
HEADERS = {'Access-Control-Allow-Origin': '*'}


Compress(app)


class FileNotAllowUpload(Exception):
    pass


def allowed_file(filename):
    return True


def load_array(str_array):
    logger.debug(f"load array: \"{str_array}\"")
    return json_tricks.loads(str_array)


def read_from_request(inp_request):
    "read_from_request"
    print('files:', inp_request.files)
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
        raise FileNotAllowUpload()
    form = inp_request.form
    format = form.get('read_format', None)
    filename = form.get('read_filename', filename)
    index = form.get('read_index', None)
    data_array = load_array(form.get('data', '{}'))
    data_calc_array = load_array(form.get('calc_data', '{}'))
    logger.debug(f"filename: {filename}")
    logger.debug(f"data_array: {data_array}")
    logger.debug(f"data_calc_array: {data_calc_array}")
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
        # gaseio.regularize.regularize_arrays(arrays)
    elif isinstance(arrays, list):
        for arr in arrays:
            arr['filename'] = filename
            arr.update(data_array)
            if not 'calc_arrays' in arr:
                arr['calc_arrays'] = dict()
            arr['calc_arrays'].update(data_calc_array)
            # gaseio.regularize.regularize_arrays(arr)
    logger.debug(f"filename: {filename}")
    logger.debug(f"arrays: {arrays}")
    logger.debug(json_tricks.dumps(arrays, indent=4, allow_nan=True))
    return arrays


# @app.route('/read', methods=['POST'])
# @app.route('/parse', methods=['POST'])
# def app_read():
#     "app_read"
#     arrays = read_from_request(request)
#     return Response(json_tricks.dumps(arrays, allow_nan=True), mimetype="application/json")


def write_with_request(inp_request, arrays):
    "write_with_request"
    form = inp_request.form
    filename = form.get('write_filename', None)
    fileformat = form.get('write_format', None)
    logger.debug(f"{form}\n{filename}\n{fileformat}")
    if not filename and not fileformat:
        msg = 'filename and format cannot be None at the same time'
        raise NotImplementedError(msg)
    if fileformat == 'json':
        return json_tricks.dumps(arrays, allow_nan=True)
    if filename:
        if isinstance(arrays, dict):
            arrays['filename'] = filename
        elif isinstance(arrays, list):
            for arr in arrays:
                arr['filename'] = filename
    logger.debug(f"filename: {filename}")
    output = gaseio.get_write_content(
        filename, arrays, fileformat, force_gase=True)
    return output


@app.route('/convert', methods=['POST'])
def app_convert():
    "app_convert"
    try:
        arrays = read_from_request(request)
        output = write_with_request(request, arrays)
        res = {
            'success': True,
            'message': '',
            'data': output,
        }
    except Exception as e:
        res = {
            'success': False,
            'message': f"{e}",
            'data': '',
        }
    return res


@app.route('/html_convert', methods=['POST'])
def app_html_convert():
    "app_html_convert"
    output = app_convert()
    if isinstance(output, Response):
        return output
    return Response(output, mimetype="text/plain", headers=HEADERS)


# @app.route('/')
# def index():
#     return send_from_directory(HTMLDIR, "index.html")


def valid_port(hostname='127.0.0.1', starting_port=5000):
    import socket
    from contextlib import closing
    _port = starting_port
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind((hostname, _port))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error:
        _port += 1
    return _port


if __name__ == '__main__':
    import argparse
    import werkzeug.serving
    localhost = '127.0.0.1'
    DEFAULT_GASEIO_PORT = 5001
    port = int(os.environ.get("GASEIO_PORT", DEFAULT_GASEIO_PORT))
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if not werkzeug.serving.is_running_from_reloader():
        logger.setLevel(logging.INFO)

        localhost = '127.0.0.1'
        port = valid_port(starting_port=port)
        logger.info(f"port: {port}")
        os.environ['GASEIO_PORT'] = str(port)
    else:
        logger.info(
            f"\n\nexport CHEMIO_SERVER_URLS=http://{localhost}:{port}\n\n")
    app.run(host=localhost, port=port, debug=args.debug)
