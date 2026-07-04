"""Warema WMS WebControl integration for Home Assistant."""
import logging
import threading

_LOGGER = logging.getLogger(__name__)

CONF_WEBCONTROL_SERVER_ADDR = 'webcontrol_server_addr'
CONF_UPDATE_INTERVAL = 'update_interval'


def get_or_init_shades(hass, config):
    """Initialize shades once, shared across all platforms.

    Uses a threading lock to ensure only one platform triggers
    the (slow) hardware discovery, even when multiple platforms
    start concurrently.
    """
    from .warema_wms import Shade, WmsController

    if 'warema_shades_lock' not in hass.data:
        hass.data['warema_shades_lock'] = threading.Lock()

    with hass.data['warema_shades_lock']:
        if 'warema_shades' not in hass.data:
            _LOGGER.info("Discovering Warema WMS shades...")
            hass.data['warema_shades'] = Shade.get_all_shades(
                WmsController(config[CONF_WEBCONTROL_SERVER_ADDR]),
                time_between_cmds=0.5
            )
            _LOGGER.info(
                "Found %d Warema devices", len(hass.data['warema_shades'])
            )

    return hass.data['warema_shades']