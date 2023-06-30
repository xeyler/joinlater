import logging
from getpass import getpass

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


class PrivateKeyCertPair():
    @classmethod
    def generate(cls):
        new_private_key = rsa.generate_private_key(
            key_size=2048,
            public_exponent=65537
        )
        return cls(new_private_key, cert=None)

    @classmethod
    def from_pkcs12(cls, path):
        cls.verify_file_exists(path)

        pkcs12_bundle = cls.load_password_protected_key(
            path, serialization.pkcs12.load_pkcs12)
        return cls(pkcs12_bundle.key, pkcs12_bundle.cert.certificate)

    @classmethod
    def from_pem_files(cls, key_path, cert_path):
        cls.verify_file_exists(key_path)
        cls.verify_file_exists(cert_path)

        private_key = cls.load_password_protected_key(
            key_path, serialization.load_pem_private_key
        )
        cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
        return cls(private_key, cert)

    @classmethod
    def load_password_protected_key(cls, key_path, load_method, password=None):
        try:
            return load_method(key_path.read_bytes(), password)
        except ValueError as e:
            if password is not None:
                logger.error(str(e))
            # If we couldn't load the file before, recurse with password
            # supplied by user
            password = getpass(f'Password for {key_path}: ').encode()
            return cls.load_password_protected_key(
                key_path, load_method, password)

    def verify_file_exists(path):
        if not path.is_file():
            logger.error(f"'{path}' is not a file")
            raise SystemExit(1)

    def __init__(self, private_key, cert):
        self._private_key = private_key
        self._cert = cert

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

    def save_as_pem_files(self, output_path):
        private_key_output = output_path.with_suffix('.key')
        private_key_output.write_bytes(self._private_key.private_bytes(
            encoding=Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
        cert_output = output_path.with_suffix('.crt')
        cert_output.write_bytes(self._cert.public_bytes(Encoding.PEM))
