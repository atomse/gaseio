"""


tornado server serving flask app


"""


import os
import argparse
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from gaseio.app import app

DEFAULT_GASEIO_PORT = 5000
DEFAULT_GASEIO_MAX_CORE = 4
PORT = os.environ.get("GASEIO_PORT", DEFAULT_GASEIO_PORT)
MAX_CORE = int(os.environ.get("GASEIO_MAX_CORE", DEFAULT_GASEIO_MAX_CORE))


def main(address: str = '127.0.0.1', port: int = PORT,
         max_core: int = MAX_CORE):
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(PORT, '127.0.0.1')
    http_server.start(max_core)
    # IOLoop.instance().start()
    IOLoop.current().start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', type=int, default=PORT)
    parser.add_argument('-n', '--max-core', type=int, default=MAX_CORE)
    args = parser.parse_args()
    main(args.address, args.port, args.max_core)
