import config
from securew2api import SecureW2ApiMediator
from crypto import PrivateKeyCertPair

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

logger = logging.getLogger(__name__)

argparser = ArgumentParser(
    description="Connect to Utah State University's eduroam network.")

argparser.add_argument('--loglevel', default='INFO')
argparser.add_argument('--renew', nargs='+', default=[])
args = argparser.parse_args()

numeric_level = getattr(logging, args.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    logger.error('Invalid log level: %s' % args.loglevel)
    raise SystemExit(1)

logging.basicConfig(
    level=numeric_level,
    format="%(message)s",
    stream=sys.stdout)

if __name__ == '__main__':
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

    new_identity.set_der_cert(certificate)
    new_identity.save_as_pem_files(Path('usu-eduroam-ident'))

    Path('securew2-CA-ident.crt').write_text(config.SECUREW2_CA_CERTIFICATE)

    print(f'Identity: {new_identity.get_cert_common_name()}')
    print(f'Domain: {config.CONNECTION_DOMAIN}')
