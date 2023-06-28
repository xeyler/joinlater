from securew2api import SecureW2ApiMediator
from crypto import PrivateKey

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

logger = logging.getLogger(__name__)

argparser = ArgumentParser(
    description="Connect to Utah State University's eduroam network.")

argparser.add_argument('--loglevel', default='WARNING')
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

new_private_key = PrivateKey()

keys_to_unenroll = []
for key_file in args.renew:
    if not Path(key_file).exists():
        logger.error('Keyfile does not exist: %s', key_file)
        raise SystemExit(1)
    keys_to_unenroll.append(PrivateKey(Path(key_file)))
logger.debug('Keys to be unenrolled: %s',
             [str(path) for path in keys_to_unenroll])

mediator = SecureW2ApiMediator()

certificate = mediator.create_certificate(new_private_key, keys_to_unenroll)

new_private_key.set_der_cert(certificate)
new_private_key.save_as_pem_files(
    Path('usu-eduroam-ident')
)

logging.info('Finished')
