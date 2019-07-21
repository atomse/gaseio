"""


tornado server serving flask app


"""



import os
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from gaseio.app import app

DEFAULT_GASEIO_PORT = 5000
port = os.environ.get("GASEIO_PORT", DEFAULT_GASEIO_PORT)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(port)
IOLoop.instance().start()
