# -*- coding: utf-8 -*-

import os
# import re
# import hashlib
import modlog
from werkzeug.utils import secure_filename
from flask import Flask
from flask import request
from flask import jsonify
# from flask import send_from_directory
from flask import Response
from flask_compress import Compress

import glob
import json_tricks
import atomtools.name
import gaseio
import pubchempy

logger = modlog.getLogger(__name__, 'normal', 'GASEIO_APP_LOGLEVEL')


UPLOAD_DIR = os.environ.get("GASEIO_UPLOAD_DIR",
                            os.path.expanduser('~/chemio'))
SOURCE = '5dNHn71A8zDrC7xec1UwNcIIMYXbq8U4L2h10zd40v1353Ml0QgoHCAow2v7aH7WbJ4K2OjGQEN7s4zEeQcyWNGpK16gZsmALie'
STORE_FILE = os.environ.get("GASEIO_STORE_FILE", 'True').upper() == 'TRUE'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


app = Flask(__name__, static_url_path='/static')
BASEDIR = os.path.dirname(os.path.realpath(__file__))
HTMLDIR = os.path.join(BASEDIR, 'html')
HEADERS = {}


Compress(app)


class FileNotAllowUpload(Exception):
    pass


def allowed_file(filename):
    return True


def load_array(str_array):
    logger.debug(f"load array: \"{str_array}\"")
    if str_array is None:
        return {}
    return json_tricks.loads(str_array)


def store_this_file(source=None):
    if not STORE_FILE:
        return False
    if source == SOURCE:
        return False
    return True


def get_file_md5sum(fileobj):
    """
    get md5sum of a file
    """
    import hashlib
    if isinstance(fileobj, bytes):
        data = fileobj
    elif isinstance(fileobj, str):
        if os.path.isfile(fileobj):
            with open(fileobj, 'rb') as fp:
                data = fp.read()
        else:
            data = fileobj.encode()
    else:
        raise ValueError('get_file_md5sum get a string/bytes')
    file_md5 = hashlib.md5(data).hexdigest()
    return file_md5

def get_basename_with_md5sum(md5sum):
    assert len(md5sum) == 32, 'invalid md5sum'
    dest_filename = os.path.join(UPLOAD_DIR, md5sum[:2], md5sum[2:4], f'{md5sum}_')
    return dest_filename

def read_from_request(inp_request):
    "read_from_request"
    # set form
    form = inp_request.form
    filetoken = form.get('file_token', None)
    read_format = form.get('read_format', None)
    filename = form.get('read_filename', None)
    index = form.get('read_index', None)
    source = form.get('source', None)
    compressed = not (form.get('compressed', False)
                      in ['False', False, 'false'])
    data_array = load_array(form.get('data', '{}'))
    data_calc_array = load_array(form.get('calc_data', '{}'))
    # set files
    logger.debug(f'files: {inp_request.files}')
    upload_file = inp_request.files['read_file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        # 将文件保存到 static/uploads 目录，文件名同上传时使用的文件名
        # dest_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        file_content = upload_file.read().strip()
        # get md5sum of the file
        md5sum = get_file_md5sum(file_content)
        basename = get_basename_with_md5sum(md5sum)
        glob_res = glob.glob(basename + '*')
        # print(glob_res)
        if glob_res:
            dest_filename = glob_res[0]
        else:
            dest_filename = basename + f'{filename}'
            if compressed:
                dest_filename += '.gz'
            dirname = os.path.dirname(dest_filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname, exist_ok=True)
            with open(dest_filename, 'wb') as fd:
                fd.write(file_content)
    else:
        raise FileNotAllowUpload()
    logger.debug(
        f"filename: {filename}\n\
          data_array: {data_array}\n\
          data_calc_array: {data_calc_array}")
    if index == 'on':
        index = ':'
    elif index == 'off' or index is None:
        index = -1
    arrays = gaseio.read(dest_filename, index, read_format, force_gase=True)
    if isinstance(arrays, dict):
        arrays['filename'] = filename
        if data_array:
            arrays.update(data_array)
        if not 'calc_arrays' in arrays:
            arrays['calc_arrays'] = dict()
        if data_calc_array:
            arrays['calc_arrays'].update(data_calc_array)
        # gaseio.regularize.regularize_arrays(arrays)
    elif isinstance(arrays, list):
        for arr in arrays:
            arr['filename'] = filename
            if data_array:
                arr.update(data_array)
            if not 'calc_arrays' in arr:
                arr['calc_arrays'] = dict()
            if data_calc_array:
                arr['calc_arrays'].update(data_calc_array)
            # gaseio.regularize.regularize_arrays(arr)
    if not store_this_file(source):
        os.remove(dest_filename)
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
    if filename:
        if isinstance(arrays, dict):
            arrays['filename'] = filename
        elif isinstance(arrays, list):
            for arr in arrays:
                arr['filename'] = filename
    logger.debug(f"filename: {filename}")
    if fileformat == 'json':
        output = json_tricks.dumps(arrays, allow_nan=True)
    else:
        output = gaseio.get_write_content(
            filename, arrays, fileformat, force_gase=True)
    logger.debug(f"write_with_request: output: {output}")
    return output


@app.route('/upload', methods=['POST'])
def upload_file():
    upload_file = request.files['file']
    form = request.form
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        dest_filename = os.path.join(
            UPLOAD_DIR, atomtools.name.randString() + '_' + filename)
        compressed = not (form.get('compressed', False)
                          in ['False', False, 'false'])
        if compressed:
            dest_filename += '.gz'
        upload_file.save(dest_filename)
        res = {
            'code': 20000,
            'message': 'success',
            'data': {
                'filename': dest_filename
            },
        }
    else:
        res = {
            'code': 50100,
            'message': 'upload fail',
            'data': {},
        }
    return jsonify(res)


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
        logger.debug(f"{e}")
        res = {
            'success': False,
            'message': f"{e}",
            'data': '',
        }
    res = json_tricks.dumps(res, allow_nan=True)
    logger.debug(f'res: {res}')
    return Response(res, content_type='application/json', headers=HEADERS)


@app.route('/get_molecule', methods=['POST'])
def get_molecule():
    """get molecule"""
    from gaseio.format_string.pubchem import parse_pubchem_json
    try:
        identifier = request.form['id']
        namespace = request.form.get('type', 'formula')
        record_type = request.form.get('record_type', '3d')
        assert namespace in ['formula',
                             'name'], "namespace must be 'formula' or 'name'"
        results = pubchempy.get_compounds(
            identifier, namespace, record_type=record_type)
        data = []
        for r in results:
            data.append(parse_pubchem_json(r.__dict__, index=0))
        res = {
            'code': 200,
            'success': True,
            'message': '',
            'data': data,
        }
    except AssertionError as e:
        res = {
            'code': 500,
            'success': False,
            'message': f"{e}",
            'data': '',
        }
    except pubchempy.BadRequestError as e:
        res = {
            'code': 510,
            'success': False,
            'message': f"{e}",
            'data': '',
        }
    return Response(json_tricks.dumps(res, allow_nan=True),
                    content_type='application/json', headers=HEADERS)


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
    # HEADERS = {'Access-Control-Allow-Origin': '*'}
    if not werkzeug.serving.is_running_from_reloader():
        localhost = '127.0.0.1'
        port = valid_port(starting_port=port)
        logger.info(f"port: {port}")
        os.environ['GASEIO_PORT'] = str(port)
    else:
        logger.info(
            f"\n\nexport CHEMIO_SERVER_URL=http://{localhost}:{port}/convert\n\n")
    app.run(host=localhost, port=port, debug=args.debug)
