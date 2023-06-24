from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import secrets
import logging

logger = logging.getLogger(__name__)

__version__ = '0.1'


class HTTPCallbackServer(HTTPServer):

    def __init__(self, secret=secrets.token_hex(32), bind_addr='localhost', port=0):
        super().__init__((bind_addr, port), HTTPCallbackRequestHandler)
        self.stopped = False
        self.callback_response = None
        self.secret = secret

    def listen(self):
        logger.debug(
            'Web server bound to %s waiting for secret "%s" to appear in '
            'requested URL...', self.server_address, self.secret)
        while not self.stopped:
            self.handle_request()
        return self.callback_response


class HTTPCallbackRequestHandler(BaseHTTPRequestHandler):

    server_version = 'SimpleCallbackServer/' + __version__

    def do_GET(self):
        if self.server.secret in self.path:
            logger.debug('Accepted path: %s', self.path)
            self.server.callback_response = self.path
            self.server.stopped = True
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Done! You may now close this window.')
        else:
            # If the client didn't pass the secret somewhere in the path,
            # pretend to be a teapot... Maybe they'll go away?
            self.send_response(HTTPStatus.IM_A_TEAPOT)
            self.end_headers()

    def log_message(self, message, *args):
        logger.debug(message, *args)
