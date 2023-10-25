import logging
import sdbus
from uuid import uuid4
from sdbus_block.networkmanager import NetworkManagerSettings
from sdbus_block.networkmanager import NetworkManagerConnectionProperties

from joinlater.networking.mediator import (
    NetworkConfigurationMediator,
    WPA2EnterpriseConnectionSettings)

logger = logging.getLogger(__name__)

class NetworkManagerMediator(NetworkConfigurationMediator):
    def add_connection(connection_settings: WPA2EnterpriseConnectionSettings) -> bool:
        sdbus.set_default_bus(sdbus.sd_bus_open_system())

        if NetworkManagerSettings().get_connections_by_id(connection_settings.ssid):
            logger.warning(
                f'Refusing to configure NetworkManager because connection '
                f'"{connection_settings.ssid}" already exists!')
            return False

        ca_cert_path = "file://" + \
            str(connection_settings.ca_cert_path) + "\0"
        ca_cert_path = ca_cert_path.encode("utf-8")
        private_cert_path = "file://" + \
            str(connection_settings.private_cert_path) + "\0"
        private_cert_path = private_cert_path.encode("utf-8")
        private_key_path = "file://" + \
            str(connection_settings.private_key_path) + "\0"
        private_key_path = private_key_path.encode("utf-8")

        properties: NetworkManagerConnectionProperties = {
            "connection": {
                "id": ("s", connection_settings.ssid),
                "uuid": ("s", str(uuid4())),
                "type": ("s", "802-11-wireless"),
                "autoconnect": ("b", True)
            },
            "802-1x": {
                "identity": ("s", connection_settings.identity),
                "domain-suffix-match": ("s", connection_settings.domain),
                "eap": ("as", ["tls"]),
                "ca-cert": ("ay", ca_cert_path),
                "client-cert": ("ay", private_cert_path),
                "private-key": ("ay", private_key_path),
                "private-key-password": ("s", connection_settings.private_key_password),
                "private-key-password-flags": ("u", 0),
            },
            "802-11-wireless": {
                "mode": ("s", "infrastructure"),
                "security": ("s", "802-11-wireless-security"),
                "ssid": ("ay", connection_settings.ssid.encode("utf-8")),
            },
            "802-11-wireless-security": {
                "key-mgmt": ("s", "wpa-eap"),
            },
            "ipv4": {"method": ("s", "auto")},
            "ipv6": {"method": ("s", "auto")},
        }

        connection_settings_dbus_path = NetworkManagerSettings().add_connection(properties)
        logger.debug(properties)
        return bool(connection_settings_dbus_path)
