from joinlater.securew2api import SecureW2ApiMediator
from joinlater.securew2config import SecureW2Config
from joinlater.crypto import PrivateKeyCertPair

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

logger = logging.getLogger(__name__)

argparser = ArgumentParser(
    description="Connect to Utah State University's eduroam network.")

argparser.add_argument(
    '--loglevel', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
    default='INFO')
argparser.add_argument(
    '--renew', nargs='+',
    help="Private key/user cert pairs to renew via SecureW2",
    metavar=("user-ident.key:user-ident.crt", "user-ident.p12"), default=[])
args = argparser.parse_args()

numeric_level = getattr(logging, args.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    logger.error('Invalid log level: %s' % args.loglevel)
    raise SystemExit(1)

logging.basicConfig(
    level=numeric_level,
    format="%(message)s",
    stream=sys.stdout)


def run():
    new_identity = PrivateKeyCertPair.generate()

    keys_to_unenroll = []
    for key_file in args.renew:
        if ':' in key_file:
            pem_files = key_file.split(':')
            if not pem_files[0].endswith('.key'):
                pem_files.reverse()
            pem_key_file = Path(pem_files[0])
            pem_cert_file = Path(pem_files[1])
            keys_to_unenroll.append(
                PrivateKeyCertPair.from_pem_files(pem_key_file, pem_cert_file))
        else:
            keys_to_unenroll.append(PrivateKeyCertPair.from_pkcs12(Path(key_file)))

    while True:
        securew2_url = input("Input your organization's SecureW2 URL: ")

        config_url = securew2_url + '/linux/SecureW2.cloudconfig'
        config = SecureW2Config.from_URL(config_url)

        confirmation = input(f'Associate with {config.organization_title}? '
            '[y/N] ')
        if confirmation.lower() in ('y', 'yes'):
            break

    mediator = SecureW2ApiMediator(config)

    certificate = mediator.create_certificate(new_identity, keys_to_unenroll)

    new_identity.set_der_cert(certificate)
    new_identity.save_as_pem_files(Path('eduroam-ident'))

    Path('securew2-CA-ident.crt').write_text(config.ca_certificate)

    print(
        'Wrote user private key, user certificate, and CA certificate to '
        'current directory.')
    print(
        'You may now configure your networking software to connect to '
        'eduroam.')
    print(f'Identity: {new_identity.get_cert_common_name()}')
    print(f'Domain: {config.eap_server}')


if __name__ == '__main__':
    run()
