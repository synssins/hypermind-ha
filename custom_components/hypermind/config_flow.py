"""Config flow for Hypermind integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    base_url = f"http://{host}:{port}"
    
    session = async_get_clientsession(hass)
    
    try:
        async with async_timeout.timeout(10):
            # Try the API endpoint
            async with session.get(f"{base_url}/api/stats") as response:
                if response.status != 200:
                    raise CannotConnect(f"HTTP {response.status}")
                data = await response.json()
                if "count" not in data:
                    raise CannotConnect("Invalid API response")
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Cannot connect: {err}") from err
    except TimeoutError as err:
        raise CannotConnect("Connection timeout") from err

    return {"title": f"Hypermind ({host}:{port})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hypermind."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check for duplicate entries
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
