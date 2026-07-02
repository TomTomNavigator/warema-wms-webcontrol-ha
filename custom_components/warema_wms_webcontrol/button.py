import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.button import ButtonEntity
from .cover import CONF_WEBCONTROL_SERVER_ADDR

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    from .warema_wms import Shade, WmsController
    shades = Shade.get_all_shades(WmsController(config[CONF_WEBCONTROL_SERVER_ADDR]), time_between_cmds=0.5)
    
    # We only add devices that are scenes
    add_devices(WaremaSceneButton(s) for s in shades if s.is_scene)


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
        return f"{self.shade.get_room_name()} {self.shade.get_channel_name()}"

    def press(self) -> None:
        """Press the button to activate the scene."""
        # Typically scenes on WebControl are activated by sending a move command (position 100 or 0).
        # Assuming sending TX_MOVE_SHADE with some parameters triggers it.
        # We will use set_shade_position(100) which triggers the TX_MOVE_SHADE packet.
        _LOGGER.debug(f"Activating scene: {self.name}")
        self.shade.set_shade_position(100)
