import logging
from urllib.parse import urlparse
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_WEBCONTROL_SERVER_ADDR, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WEBCONTROL_SERVER_ADDR, default="http://webcontrol.local"): str,
        vol.Optional(CONF_UPDATE_INTERVAL, default=600): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect."""
    url = data[CONF_WEBCONTROL_SERVER_ADDR]
    
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise InvalidURL

    # Test the connection to the gateway
    def test_connection():
        from .warema_wms.wms_controller import WmsController
        import requests
        try:
            ctrl = WmsController(url)
            # The init of WmsController attempts to retrieve the setup
            # If it fails, it will raise an exception
            if not ctrl.rooms:
                raise CannotConnect
        except requests.exceptions.RequestException:
            raise CannotConnect
        except Exception:
            raise CannotConnect

    await hass.async_add_executor_job(test_connection)

    # Return info that you want to store in the config entry.
    return {"title": "Warema WMS"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Warema WMS WebControl."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidURL:
                errors["base"] = "invalid_url"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidURL(HomeAssistantError):
    """Error to indicate the URL is invalid."""
