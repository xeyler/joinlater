import logging
from getpass import getpass

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


class PrivateKey():
    def __init__(self, pkcs12_path=None, password=None):
        if pkcs12_path is None:
            # Generate an RSA private key with the same values that Secure W2
            # uses
            self._private_key = rsa.generate_private_key(
                key_size=2048,
                public_exponent=65537
            )
        elif pkcs12_path.suffix in ['.p12', '.pfx']:
            try:
                pkcs12_bundle = pkcs12.load_pkcs12(
                    pkcs12_path.read_bytes(),
                    password
                )
                self._private_key = pkcs12_bundle.key
                self._cert = pkcs12_bundle.cert.certificate
            except ValueError as e:
                if password is not None:
                    logger.error(str(e))
                # If we couldn't load the file before, try again after
                # prompting for a password
                password = getpass(f'Password for {pkcs12_path}: ').encode()
                self.__init__(pkcs12_path, password=password)
        else:
            logger.error(
                'Unrecognized private key format: %s',
                pkcs12_path.suffix)
            raise SystemExit(1)

    def create_csr(self):
        builder = x509.CertificateSigningRequestBuilder()
        builder = builder.subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, u'anonymous'),
            ]))
        csr = builder.sign(
            self._private_key, hashes.SHA256()
        )
        return csr.public_bytes(serialization.Encoding.DER)

    def sign(self, data):
        return self._private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def get_public_key(self):
        return self._private_key.public_key()

    def get_der_cert(self):
        return self._cert.public_bytes(serialization.Encoding.DER)

    def set_der_cert(self, cert_bytes):
        self._cert = x509.load_der_x509_certificate(cert_bytes)

    def save_as_pkcs12(self, name, pkcs12_path):
        while True:
            password = getpass('Enter a password to encrypt private key: ').encode()
            confirmation = getpass('Re-enter password: ').encode()
            if password == confirmation:
                break
            print("Passwords don't match! Try again.")

        pkcs12_path.write_bytes(pkcs12.serialize_key_and_certificates(
            name=name.encode('utf-8'), key=self._private_key, cert=self._cert,
            cas=None, encryption_algorithm=serialization.BestAvailableEncryption(password)
        ))
