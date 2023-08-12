from furl import furl

from joinlater.simplehttpcallback import HTTPCallbackServer

import secrets
from hashlib import sha1


class SecureW2Oauth():
    @staticmethod
    def authenticate(config):
        http_callback = HTTPCallbackServer()

        oauth_url = furl(config.sso_url)
        # NOTE: SecureW2's Oauth functions ONLY with localhost, not 127.0.0.1
        # or any other domain/IP. HTTPS is allowed on localhost, but securing
        # the connection shouldn't be necessary. If a 3rd party has access to
        # localhost, you're already pwned. The official client does this too.
        oauth_url.args['redirect_uri'] = f'http://localhost:{http_callback.server_port}/'
        oauth_url.args['state'] = http_callback.secret

        print(f'Authenticate with your account: {oauth_url}')

        response = furl(http_callback.listen())
        # Expect the returned path to contain exactly one 'code' query parameter
        return response.args['code']


class PrivateKeySignChallenge():
    def __init__(self, id, private_key, challenge_bytes):
        self.id = id
        self.client_nonce = secrets.token_bytes(64)
        nonces_digest = sha1(challenge_bytes + self.client_nonce).digest()
        self.signed_nonces = private_key.sign(nonces_digest)
