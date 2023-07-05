from base64 import b64encode, b64decode
import json
import logging
import secrets
from hashlib import sha1

import requests
from requests import ConnectTimeout, ReadTimeout

import config
from identityproviders import PrivateKeySignChallenge, SecureW2Oauth

logger = logging.getLogger(__name__)

API_VERSION = '1.4'


class SecureW2ApiMediator():
    ENDPOINT_URL = config.SECUREW2_PKI_ENDPOINT_URL

    def __init__(self):
        self.check_version()

    def send_request(self, request, timeout=10, check_for_errors=True):
        response = None
        try:
            response = requests.post(
                self.ENDPOINT_URL, json=request.payload, timeout=20)
            response.raise_for_status()
            json_response = response.json()
            if check_for_errors and json_response['error'] != 0:
                raise ValueError('API reported error!')
            return json_response
        except (ConnectTimeout, ReadTimeout) as e:
            logger.error('SecureW2 API took too long to respond')
            raise SystemExit(1) from e
        except requests.HTTPError as e:
            logger.error(
                'SecureW2 API returned unexpected status code: %s',
                response.reason)
            raise SystemExit(1) from e
        except requests.JSONDecodeError as e:
            logger.error('SecureW2 API responded with malformed json')
            raise SystemExit(1) from e
        except requests.ConnectionError as e:
            logger.error(
                'Could not connect to SecureW2 endpoint. '
                'Are you connected to the internet?')
            raise SystemExit(1) from e
        finally:
            if response is not None:
                logger.debug('sent: %s', response.request.body.decode('utf-8'))
                logger.debug('received: %s', response.text)

    def create_certificate(self, private_key, old_keys):
        oauth_code = SecureW2Oauth.authenticate()

        logger.debug('Requesting certificate signature from Secure W2...')
        old_certs = [key.get_der_cert() for key in old_keys]

        challenge_response = self.send_request(ChallengeRequest(old_certs))
        signing_challenges = []
        for key in old_keys:
            id = ChallengeRequest.get_cert_id(key.get_der_cert())
            challenge = challenge_response['challenges'][id]
            signing_challenges.append(
                PrivateKeySignChallenge(id, key, b64decode(challenge))
            )
        transaction_id = challenge_response['transaction-id']

        csr = private_key.create_csr()

        enroll_reponse = self.send_request(
            EnrollRequest(
                oauth_code, signing_challenges, transaction_id, csr, old_certs
            )
        )

        signed_certs = enroll_reponse['signedCertificates']

        logger.debug('Successfully retrieved certificate!')
        # I'm not sure why, but the API seemingly allows the user to submit
        # multiple certificate signing requests in one request. Thus, it
        # returns a list of signed certificates on success. We're only
        # interested in the first one as we only submitted one CSR.
        return b64decode(signed_certs[0])

    def check_version(self):
        logger.debug('Checking Secure W2 API version...')
        response = self.send_request(VersionRequest(), check_for_errors=False)
        if response['version'] != API_VERSION:
            logger.error(
                'Secure W2 API is of incompatible version: %s',
                response['version'])
            raise SystemExit(1)
        else:
            logger.debug(f'Version {response["version"]} accepted')


class Request():
    def __init__(self):
        self.payload = {'version': API_VERSION}


class VersionRequest(Request):
    def __init__(self):
        super().__init__()
        self.payload |= {'type': 'getVersion'}


class ChallengeRequest(Request):
    def __init__(self, certs):
        super().__init__()
        self.payload |= {'type': 'challengeRequest'}
        requests = [
            {'name': self.get_cert_id(cert), 'length': 64} for cert in certs
        ]
        self.payload |= {'requests': requests}

    @staticmethod
    def get_cert_id(der_cert):
        # For real, Secure W2?
        return 'ClientCert' + sha1(der_cert).hexdigest() + '-Challenge'


class EnrollRequest(Request):
    def __init__(
            self, oauth_code, key_challenges, transaction_id, csr,
            old_der_certs):
        super().__init__()
        self.payload |= {'type': 'enroll' if old_der_certs == [] else 'renew'}
        # The official client sets identity to an empty string when using Oauth
        # Why? That's a question I've grown accustomed to not having answered
        self.payload |= {'identity': ''}
        oauth_challenge = {'type': 0, 'value': oauth_code}
        prepped_key_challenges = [
            {
                'type': 1,
                'challenge': signature.id,
                'clientNonce':
                    b64encode(signature.client_nonce).decode('utf-8'),
                'value':
                    b64encode(signature.signed_nonces).decode('utf-8')
            } for signature in key_challenges
        ]
        challenge_json = json.dumps([oauth_challenge] + prepped_key_challenges)
        self.payload |= {
            'challenge':
                b64encode(challenge_json.encode('utf-8')).decode('utf-8')
        }
        self.payload |= {'transaction-id': transaction_id}
        self.payload |= {
            'certificateRequests': [b64encode(csr).decode('utf-8')]
        }
        self.payload |= {
            'clientCertificate':
                [b64encode(cert).decode('utf-8') for cert in old_der_certs]
        }
        self.payload |= {'deviceAttributes': {
            # The official client gets the client ID by concatenating
            # /sys/class/dmi/id/modalias and /var/lib/dbus/machine-id and sha1
            # hashing the result. There are some fallbacks. It gets weird.
            # See reporter.py, gendeviceid() from the official client
            #
            # Anyways, setting the client ID to a random value each time we run
            # this script may cause us to accrue unused certificates,
            # effectively making Secure W2 think that we have many more devices
            # enrolled than we actually do.
            #
            # Hopefully this is a non-issue for three reasons:
            #  1. Secure W2 should know to remove old certs because of the
            #     signing challenge/old certs we send alongside our CSR
            #  2. Whoever uses this script typically won't be using it multiple
            #     times to generate one cert for one device. Especially since
            #     Secure W2 CA makes certs valid for *checks notes* 5 years...
            #  3. As a fallback, the official client will generate this value
            #     using random data when the sysfs objects it relies on are
            #     nowhere to be found. And if Secure W2 does something, then it
            #     must be a good, smart, safe, sane thing to do.
            #
            # If my assumptions prove false, USU IT gets alerts on some
            # dashboard, they contact Secure W2, Secure W2 finds me out, I get
            # prosecuted somehow for stealing intellectual property or
            # something, and I spend the rest of my days in jail with free
            # housing and meals.
            #
            # Really, it's a win-win either way.
            'clientId': secrets.token_hex(20),
            'adapters': {'wireless': []},
            'applicationFriendlyName': 'JoinLater for Linux',
            'applicationVersion': '3.14',
            'buildModel': '',
            'computerIdentity': '',
            'operatingSystem': '',
            'osArchitecture': '',
            'osVersion': '',
            'osVersionFriendlyName': '',
            'userDescription': ''}
        }
        self.payload |= {'configInfo': {
            'profileId': config.DEVICE_CONFIG_PROFILE_UUID,
            'deviceConfigName': config.DEVICE_CONFIG_NAME,
            'organizationId': config.ORGANIZATION_UID
        }}
