"""Config flow for Hypermind integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    CONF_SCALE_MIN,
    CONF_SCALE_MAX,
    DEFAULT_SCALE_MIN,
    DEFAULT_SCALE_MAX,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCALE_MIN, default=DEFAULT_SCALE_MIN): vol.Coerce(int),
        vol.Optional(CONF_SCALE_MAX, default=DEFAULT_SCALE_MAX): vol.Coerce(int),
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
            async with session.get(f"{base_url}/api/stats") as response:
                if response.status != 200:
                    raise CannotConnect(f"HTTP {response.status}")
                api_data = await response.json()
                if "count" not in api_data:
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
            # Validate scale values
            scale_min = user_input.get(CONF_SCALE_MIN, DEFAULT_SCALE_MIN)
            scale_max = user_input.get(CONF_SCALE_MAX, DEFAULT_SCALE_MAX)
            
            if scale_min >= scale_max:
                errors["base"] = "invalid_scale"
            else:
                try:
                    info = await validate_input(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Hypermind."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            scale_min = user_input.get(CONF_SCALE_MIN, DEFAULT_SCALE_MIN)
            scale_max = user_input.get(CONF_SCALE_MAX, DEFAULT_SCALE_MAX)
            
            if scale_min >= scale_max:
                errors["base"] = "invalid_scale"
            else:
                # Update the config entry with new options
                return self.async_create_entry(title="", data=user_input)
        
        # Get current values from options or data
        current_min = self.config_entry.options.get(
            CONF_SCALE_MIN,
            self.config_entry.data.get(CONF_SCALE_MIN, DEFAULT_SCALE_MIN)
        )
        current_max = self.config_entry.options.get(
            CONF_SCALE_MAX,
            self.config_entry.data.get(CONF_SCALE_MAX, DEFAULT_SCALE_MAX)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCALE_MIN, default=current_min): vol.Coerce(int),
                    vol.Optional(CONF_SCALE_MAX, default=current_max): vol.Coerce(int),
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
