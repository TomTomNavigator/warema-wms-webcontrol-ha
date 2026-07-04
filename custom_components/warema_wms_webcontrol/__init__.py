"""Warema WMS WebControl integration for Home Assistant."""
import logging
import threading

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN, CONF_WEBCONTROL_SERVER_ADDR, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER, Platform.NUMBER, Platform.BUTTON]


def get_or_init_shades(hass, server_addr):
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
                WmsController(server_addr),
                time_between_cmds=0.5
            )
            _LOGGER.info(
                "Found %d Warema devices", len(hass.data['warema_shades'])
            )

    return hass.data['warema_shades']


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration via YAML (legacy)."""
    # Just initialize the dictionary for our domain
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Warema WMS WebControl from a config entry."""
    
    server_addr = entry.data.get(CONF_WEBCONTROL_SERVER_ADDR)

    # Initialize the shades in an executor job because it blocks
    await hass.async_add_executor_job(get_or_init_shades, hass, server_addr)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        # Clear out the shared shade state so a reload triggers a fresh discovery
        if not hass.data[DOMAIN]:
            hass.data.pop('warema_shades', None)
            hass.data.pop('warema_shades_lock', None)

    return unload_ok