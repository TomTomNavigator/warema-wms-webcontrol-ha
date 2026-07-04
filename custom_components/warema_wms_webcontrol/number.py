import logging

from homeassistant.components.number import NumberEntity
from .cover import CONF_WEBCONTROL_SERVER_ADDR

_LOGGER = logging.getLogger(__name__)

import logging
_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    from .warema_wms import Shade, WmsController
    import threading
    
    _LOGGER.error("NUMBER PLATFORM STARTING UP!")
    
    if 'warema_shades_lock' not in hass.data:
        hass.data['warema_shades_lock'] = threading.Lock()
        
    with hass.data['warema_shades_lock']:
        if 'warema_shades' not in hass.data:
            hass.data['warema_shades'] = Shade.get_all_shades(WmsController(config[CONF_WEBCONTROL_SERVER_ADDR]), time_between_cmds=0.5)
            
    shades = hass.data['warema_shades']
    
    devices = [WaremaTiltNumber(s) for s in shades if not s.is_scene]
    _LOGGER.error(f"NUMBER PLATFORM ADDING DEVICES: {[d.name for d in devices]}")
    add_devices(devices)

class WaremaTiltNumber(NumberEntity):
    """Representation of a Warema tilt as a Number."""

    def __init__(self, shade):
        """Initialize the number."""
        self.shade = shade

    @property
    def unique_id(self):
        return f"warema_tilt_{self.shade.room.id}_{self.shade.channel.id}"

    @property
    def name(self):
        """Return the name of the tilt number."""
        return f"{self.shade.get_room_name()} {self.shade.get_channel_name()} Neigung"

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return 0

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return 75

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return 1

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "°"

    @property
    def native_value(self) -> float:
        """Return the current value."""
        if self.shade.tilt is not None:
            val = self.shade.tilt - 127
            # Clamp the value to prevent HA from throwing out-of-range exceptions
            if val < 0:
                return 0
            if val > 75:
                return 75
            return val
        return None

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        tilt_val = int(value) + 127
        _LOGGER.debug(f"Setting tilt for {self.name} to {value}° (raw: {tilt_val})")
        # The shade expects both position and tilt. We use the current position.
        self.shade.set_shade_position(self.shade.position, tilt_val)

    def update(self):
        """Update the shade state."""
        self.shade.get_shade_state()
