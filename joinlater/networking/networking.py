import sdbus
import logging

from joinlater.networking.mediator import NetworkConfigurationMediator, WPA2EnterpriseConnectionSettings
from joinlater.networking.networkmanager import NetworkManagerMediator

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
