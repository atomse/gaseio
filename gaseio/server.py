# -*- coding: utf-8 -*-

import os
import hashlib
import json_tricks

from werkzeug.utils import secure_filename
from flask import Flask, request

import atomtools
import gaseio



UPLOAD_DIR = os.path.expanduser('~/chemio')
if not os.path.exists(UPLOAD_DIR):
    raise IOError(UPLOAD_DIR, 'not exist')


app = Flask(__name__)


MAXSIZE = 100000000
CHUNKSIZE = 1000000


# def print_error(data):
#     return data


# def get_file_and_index():
#     if 'file' not in form:
#         print_error('Not found parameter: file')
#         return
#     form_file = form['file']
#     if not form_file.file:
#         print_error('Not found parameter: file')
#         return
#     if not form_file.filename:
#         print_error('Not found parameter: file')
#         return
#     filename = os.path.basename(form_file.filename)
#     uploaded_file_path = os.path.join(UPLOAD_DIR, atomtools.name.randString() + '_' + filename)
#     start = True
#     leftsize = MAXSIZE
#     with open(uploaded_file_path.encode('utf-8'), 'wb') as fout:
#         while True:
#             chunk = form_file.file.read(CHUNKSIZE)
#             if not chunk:
#                 break
#             if start:
#                 md5 = hashlib.md5(chunk).hexdigest()
#                 start = False
#             fout.write(chunk)
#     newfilename = md5 + '_' + filename
#     dir1, dir2 = md5[:2], md5[2:4]
#     newpath = os.path.join(UPLOAD_DIR, dir1, dir2, newfilename)
#     if not os.path.exists(os.path.dirname(newpath)):
#         os.makedirs(os.path.dirname(newpath))
#     os.rename(uploaded_file_path, newpath)
#     index = form.getvalue('index')
#     return (newpath, index)

def return_msg(code, msg):
    return {
        'code' : code,
        'msg' : msg,
    }


def allowed_file(filename):
    return True


def read_from_request(inp_request):
    "read_from_request"
    upload_file = inp_request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        # 将文件保存到 static/uploads 目录，文件名同上传时使用的文件名
        # dest_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        dest_filename = os.path.join(UPLOAD_DIR, atomtools.name.randString() + '_' + filename)
        upload_file.save(dest_filename)
    else:
        return return_msg(200, 'file not allow to upload')
    form = inp_request.form
    index = form.get('index', None)
    if index == 'on':
        index = ':'
    elif index == 'off' or index is None:
        index = -1
    arrays = gaseio.read(dest_filename, index, force_gase=True)
    if isinstance(arrays, dict):
        arrays['filename'] = filename
    elif isinstance(arrays, list):
        for arr in arrays:
            arr['filename'] = filename
    if app.debug and filename:
        print(filename)
    return arrays


@app.route('/read', methods=['POST'])
def app_read():
    "app_read"
    arrays = read_from_request(request)
    return json_tricks.dumps(arrays)


def write_with_request(inp_request, arrays):
    "write_with_request"
    form = inp_request.form
    filename = form.get('filename', None)
    fileformat = form.get('format', None)
    if not filename and not fileformat:
        raise ValueError('filename and format cannot be None at the same time')
    if filename:
        if isinstance(arrays, dict):
            arrays['filename'] = filename
        elif isinstance(arrays, list):
            for arr in arrays:
                arr['filename'] = filename
    if app.debug and filename:
        print(filename)
    output = gaseio.get_write_content(filename, arrays, fileformat, force_gase=True)
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
    app.run(port=5000, debug=True)
