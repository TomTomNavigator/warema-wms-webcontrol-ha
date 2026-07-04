import logging

from homeassistant.components.button import ButtonEntity

from .const import CONF_WEBCONTROL_SERVER_ADDR
from . import get_or_init_shades

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    shades = get_or_init_shades(hass, config.get(CONF_WEBCONTROL_SERVER_ADDR))
    devices = [WaremaSceneButton(s) for s in shades if s.is_scene]
    _LOGGER.debug("Button platform adding %d devices", len(devices))
    add_devices(devices)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the button platform from a config entry."""
    server_addr = config_entry.data.get(CONF_WEBCONTROL_SERVER_ADDR)
    shades = await hass.async_add_executor_job(get_or_init_shades, hass, server_addr)
    
    devices = [WaremaSceneButton(s) for s in shades if s.is_scene]
    _LOGGER.debug("Button platform async adding %d devices", len(devices))
    async_add_entities(devices)


class WaremaSceneButton(ButtonEntity):
    """Representation of a Warema scene as a Button."""

    def __init__(self, shade):
        """Initialize the button."""
        self.shade = shade

    @property
    def unique_id(self):
        return f"warema_scene_{self.shade.room.id}_{self.shade.channel.id}"

    @property
    def name(self):
        """Return the name of the scene."""
        return (f"{self.shade.get_room_name()} "
                f"{self.shade.get_channel_name()}")

    def press(self) -> None:
        """Press the button to activate the scene."""
        _LOGGER.debug("Activating scene: %s", self.name)
        self.shade.play_scene()
