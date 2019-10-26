"""


tornado server serving flask app


"""


import os
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from gaseio.app import app

DEFAULT_GASEIO_PORT = 5000
DEFAULT_GASEIO_MAX_CORE = 4
port = os.environ.get("GASEIO_PORT", DEFAULT_GASEIO_PORT)
max_core = os.environ.get("GASEIO_MAX_CORE", DEFAULT_GASEIO_MAX_CORE)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(port, '127.0.0.1')
http_server.start(0)
# IOLoop.instance().start()
IOLoop.current().start()
