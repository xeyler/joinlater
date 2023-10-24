import sdbus

from mediator import NetworkConfigurationMediator, WPA2EnterpriseConnectionSettings
from networkmanager import NetworkManagerMediator

logger = logging.getLogger(__name__)

def add_connection(settings: WPA2EnterpriseConnectionSettings) -> bool:
    for mediator in mediators:
        try:
            if mediator.add_connection(settings):
                logger.info("Connection saved successfully!")
                return True
        except:
            pass
    return False

mediators = [
    NetworkManagerMediator
]

if __name__ == "__main__":
    sdbus.set_default_bus(sdbus.sd_bus_open_system())

    settings = WPA2EnterpriseConnectionSettings(
        "/home/xeyler/.joinlater/usu-eduroam-ident.key",
        "pass",
        "/home/xeyler/.joinlater/usu-eduroam-ident.crt",
        "/home/xeyler/.joinlater/securew2-CA-ident.crt",
        "A02242814@securew2.usu.edu",
        "eduroam.usu.edu",
        "eduroam"
    )
    if connection_dpath := add_connection(settings):
        print(f"Path of the new connection: {connection_dpath}")
    else:
        print("Error: No new connection created.")
