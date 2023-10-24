# THIS CODE WILL SCREW UP YOUR EDUROAM CONNECTION
# it will perpetually throw errors like Activation: (wifi) association took too long & Activation: (wifi) asking for new secrets
#
# TO DO
# fix perpetual errors
# remove hard coding
# integrate with joinlater

import functools
import logging
import pprint
import sdbus
from uuid import uuid4
from argparse import ArgumentParser, Namespace
from sdbus_block.networkmanager import NetworkManagerSettings
from sdbus_block.networkmanager import NetworkManagerConnectionProperties


def add_wifi_psk_connection(args: Namespace) -> str:
    """Add a temporary (not yet saved) network connection profile
    :param Namespace args: autoconnect, conn_id, psk, save, ssid, uuid
    :return: dbus connection path of the created connection profile
    """
    info = logging.getLogger().info

    # need to remove hard coded path so it works for other users
    ca_certificate_content = "file:///home/ned/.joinlater/securew2-CA-ident.crt\0"
    encoded_ca = ca_certificate_content.encode("utf-8")

    client_certificate_content = "file:///home/ned/.joinlater/usu-eduroam-ident.crt\0"
    encoded_client = client_certificate_content.encode("utf-8")

    private_key_content = "file:///home/ned/.joinlater/usu-eduroam-ident.key\0"
    encoded_key = private_key_content.encode("utf-8")

    private_key_password = "super_s3cr3t"
    domain = "eduroam.usu.edu"
    username = "A00000000@secureW2.usu.edu"

    if NetworkManagerSettings().get_connections_by_id(args.conn_id):
        print(f'Connection "{args.conn_id}" exists, remove it first')
        print(f'Run: nmcli connection delete "{args.conn_id}"')
        return ""

    properties: NetworkManagerConnectionProperties = {
        "connection": {
            "id": ("s", args.conn_id),
            "uuid": ("s", str(args.uuid)),
            "type": ("s", "802-11-wireless"),
            "autoconnect" : ("b", True)
        },
        "802-1x": {
            "identity": ("s", username),
            "domain-suffix-match": ("s", domain),
            "eap": ("as", ["tls"]),
            "ca-cert": ("ay", encoded_ca),
            "client-cert" : ("ay", encoded_client),
            "private-key" : ("ay", encoded_key),
            "private-key-password": ("s", private_key_password),
            "private-key-password-flags": ("u", 0),
        },
        "802-11-wireless": {
            "mode": ("s", "infrastructure"),
            "security": ("s", "802-11-wireless-security"),
            "ssid": ("ay", args.ssid.encode("utf-8")),
        },
        "802-11-wireless-security": {
            "key-mgmt": ("s", "wpa-eap"),
            "auth-alg": ("s", "open"),
            # "psk": ("s", args.psk),
        },
        "ipv4": {"method": ("s", "auto")},
        "ipv6": {"method": ("s", "auto")},
    }

    if hasattr(args, "interface_name") and args.interface_name:
        properties["connection"]["interface-name"] = ("s", args.interface_name)

    s = NetworkManagerSettings()
    save = True
    # save = bool(hasattr(args, "save") and args.save)
    addconnection = s.add_connection if save else s.add_connection_unsaved
    connection_settings_dbus_path = addconnection(properties)
    created = "created and saved" if save else "created"
    info(f"New unsaved connection profile {created}, show it with:")
    info(f'nmcli connection show "{args.conn_id}"|grep -v -e -- -e default')
    info("Settings used:")
    info(functools.partial(pprint.pformat, sort_dicts=False)(properties))
    return connection_settings_dbus_path


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    p = ArgumentParser(description="Optional arguments have example values:")
    conn_id = "eduroam" # change to eduroam
    # probably can remove most of these arguments??
    p.add_argument("-c", dest="conn_id", default=conn_id, help="Connection Id")
    p.add_argument("-u", dest="uuid", default=uuid4(), help="Connection UUID") # need to investigate maybe?
    p.add_argument("-s", dest="ssid", default="eduroam", help="WiFi SSID") # change to eduroam
    #p.add_argument("-p", dest="psk", default="qwerty123", help="WiFi PSK")
    p.add_argument("-i", dest="interface_name", default="", help="WiFi device")
    p.add_argument("-a", dest="auto", action="store_true", help="autoconnect")
    p.add_argument("--save", dest="save", action="store_true", help="Save")
    args = p.parse_args()
    sdbus.set_default_bus(sdbus.sd_bus_open_system())
    if connection_dpath := add_wifi_psk_connection(args):
        print(f"Path of the new connection: {connection_dpath}")
        print(f"UUID of the new connection: {args.uuid}")
    else:
        print("Error: No new connection created.")
