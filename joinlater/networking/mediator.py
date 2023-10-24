class WPA2EnterpriseConnectionSettings():
    def __init__(
            self, private_key_path, private_key_password, private_cert_path, 
            ca_cert_path, identity, domain, ssid):
        self.private_key_path = private_key_path
        self.private_key_password = private_key_password
        self.private_cert_path = private_cert_path
        self.ca_cert_path = ca_cert_path
        self.identity = identity
        self.domain = domain
        self.ssid = ssid

class NetworkConfigurationMediator:
    def add_connection(self, connection_settings: WPA2EnterpriseConnectionSettings):
        pass
