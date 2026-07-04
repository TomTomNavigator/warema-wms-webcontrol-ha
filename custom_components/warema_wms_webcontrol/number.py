import logging

from homeassistant.components.number import NumberEntity

from . import CONF_WEBCONTROL_SERVER_ADDR, get_or_init_shades

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    shades = get_or_init_shades(hass, config)
    devices = [WaremaTiltNumber(s) for s in shades if not s.is_scene]
    _LOGGER.debug("Number platform adding %d devices", len(devices))
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
        return (f"{self.shade.get_room_name()} "
                f"{self.shade.get_channel_name()} Neigung")

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
            return max(0, min(75, val))
        return None

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        tilt_val = int(value) + 127
        _LOGGER.debug(
            "Setting tilt for %s to %d° (raw: %d)",
            self.name, value, tilt_val)
        self.shade.set_shade_position(self.shade.position, tilt_val)

    def update(self):
        """Update the shade state."""
        self.shade.get_shade_state()
