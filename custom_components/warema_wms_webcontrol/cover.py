import logging
from datetime import datetime, timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.cover import (
    CoverEntity, CoverDeviceClass, CoverEntityFeature,
    ATTR_POSITION, PLATFORM_SCHEMA, ATTR_TILT_POSITION)

from .const import CONF_WEBCONTROL_SERVER_ADDR, CONF_UPDATE_INTERVAL
from . import get_or_init_shades

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_WEBCONTROL_SERVER_ADDR,
                 default='http://webcontrol.local'): cv.url,
    vol.Optional(CONF_UPDATE_INTERVAL, default=600): cv.positive_int
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    shades = get_or_init_shades(hass, config.get(CONF_WEBCONTROL_SERVER_ADDR))
    devices = [WaremaShade(s, config.get(CONF_UPDATE_INTERVAL, 600))
               for s in shades if not s.is_scene]
    _LOGGER.debug("Cover platform adding %d devices", len(devices))
    add_devices(devices)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the cover platform from a config entry."""
    # Since discovery already happened in __init__.py, get_or_init_shades is now fast
    server_addr = config_entry.data.get(CONF_WEBCONTROL_SERVER_ADDR)
    shades = await hass.async_add_executor_job(get_or_init_shades, hass, server_addr)
    
    update_interval = config_entry.data.get(CONF_UPDATE_INTERVAL, 600)
    devices = [WaremaShade(s, update_interval) for s in shades if not s.is_scene]
    _LOGGER.debug("Cover platform async adding %d devices", len(devices))
    async_add_entities(devices)


class WaremaShade(CoverEntity):
    """Represents a Warema shade."""

    def __init__(self, shade, update_interval: int):
        self.shade = shade
        self.last_position = shade.position
        self.next_state_update = datetime.now()
        # After triggering a move, force frequent updates for 15 seconds
        # so the UI reflects the new state quickly even though the slow
        # hardware might not report 'is_moving' immediately.
        self.force_update_until = datetime.now()
        self.update_interval = update_interval

    def update(self, force=False):
        if (datetime.now() > self.next_state_update
                or self.shade.is_moving
                or datetime.now() < self.force_update_until
                or force):
            self.last_position = self.shade.position
            self.shade.get_shade_state(True)
            if self.shade.state_last_updated:
                self.next_state_update = (
                    self.shade.state_last_updated
                    + timedelta(seconds=self.update_interval)
                )
            _LOGGER.debug('Update performed for %s', self.name)
        else:
            _LOGGER.debug('Update skipped for %s. Next update %s',
                          self.name, self.next_state_update)

    @property
    def device_class(self):
        return CoverDeviceClass.SHADE

    @property
    def supported_features(self):
        features = (CoverEntityFeature.OPEN
                     | CoverEntityFeature.CLOSE
                     | CoverEntityFeature.SET_POSITION)
        if self.shade.tilt is not None:
            features |= CoverEntityFeature.SET_TILT_POSITION
        return features

    @property
    def unique_id(self):
        return f"warema_shade_{self.shade.room.id}_{self.shade.channel.id}"

    @property
    def name(self):
        return f"{self.shade.get_room_name()}:{self.shade.get_channel_name()}"

    @property
    def current_cover_position(self):
        return 100 - self.shade.position

    @property
    def current_cover_tilt_position(self):
        if self.shade.tilt is not None:
            # Map Warema angle (-90 to +90) to HA tilt (0 to 100)
            return round((self.shade.tilt + 90) * 100 / 180)
        return None

    @property
    def is_opening(self):
        return (self.shade.is_moving
                and self.last_position > self.shade.position)

    @property
    def is_closing(self):
        return (self.shade.is_moving
                and self.last_position < self.shade.position)

    @property
    def is_closed(self):
        return not self.shade.is_moving and self.shade.position == 100

    def open_cover(self, **kwargs):
        self.force_update_until = datetime.now() + timedelta(seconds=15)
        tilt = -75 if self.shade.tilt is not None else None
        self.shade.set_shade_position(0, tilt)

    def close_cover(self, **kwargs):
        self.force_update_until = datetime.now() + timedelta(seconds=15)
        self.shade.set_shade_position(100, self.shade.tilt)

    def set_cover_position(self, **kwargs):
        self.force_update_until = datetime.now() + timedelta(seconds=15)
        self.shade.set_shade_position(
            100 - kwargs[ATTR_POSITION], self.shade.tilt)

    def set_cover_tilt_position(self, **kwargs):
        tilt = kwargs.get(ATTR_TILT_POSITION)
        if tilt is not None:
            self.force_update_until = datetime.now() + timedelta(seconds=15)
            # Map HA tilt (0 to 100) back to Warema angle (-90 to +90)
            tilt_val = round((tilt * 180 / 100) - 90)
            self.shade.set_shade_position(self.shade.position, tilt_val)
