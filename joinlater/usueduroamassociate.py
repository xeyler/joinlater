from joinlater import config
from joinlater.securew2api import SecureW2ApiMediator
from joinlater.crypto import PrivateKeyCertPair
from joinlater.networking import networking
from joinlater.networking.mediator import WPA2EnterpriseConnectionSettings

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

    mediator = SecureW2ApiMediator()

    certificate = mediator.create_certificate(new_identity, keys_to_unenroll)

    joinlater_home = Path.home() / Path('.joinlater')
    joinlater_home.mkdir(parents=True, exist_ok=True)

    private_key_path = joinlater_home / Path('ident.key')
    private_cert_path = joinlater_home / Path('ident.crt')
    ca_cert_path = joinlater_home / Path('ca.crt')

    new_identity.set_der_cert(certificate)
    private_key_pass = new_identity.save_as_pem_files(
        private_key_path, private_cert_path)

    ca_cert_path.write_text(config.SECUREW2_CA_CERTIFICATE)

    settings = WPA2EnterpriseConnectionSettings(
        private_key_path,
        private_key_pass,
        private_cert_path,
        ca_cert_path,
        new_identity.get_cert_common_name(),
        config.CONNECTION_DOMAIN,
        "eduroam"
    )

    if networking.add_connection(settings):
        print("Connection saved successfully!")
    else:
        print(
            'Wrote user private key, user certificate, and CA certificate to ' +
            str(joinlater_home))
        print(
            'Use the following information to manually configure your '
            'networking software to connect to eduroam.')
        print(f'Identity: {new_identity.get_cert_common_name()}')
        print(f'Domain: {config.CONNECTION_DOMAIN}')
        print(f'Private key password: {private_key_pass}')

if __name__ == '__main__':
    run()
