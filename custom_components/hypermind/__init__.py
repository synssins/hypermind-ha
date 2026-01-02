"""The Hypermind integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_SCAN_INTERVAL,
    ATTR_ACTIVE_NODES,
    ATTR_DIRECT_CONNECTIONS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hypermind from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    
    coordinator = HypermindDataUpdateCoordinator(hass, host, port)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class HypermindDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Hypermind data."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from Hypermind API."""
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(f"{self.base_url}/api/stats") as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("API response: %s", data)
                        
                        # API returns: {"count": X, "direct": Y, "id": "..."}
                        return {
                            ATTR_ACTIVE_NODES: data.get("count", 0),
                            ATTR_DIRECT_CONNECTIONS: data.get("direct", 0),
                        }
                    raise UpdateFailed(f"API returned status {response.status}")
                    
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Hypermind: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with Hypermind: {err}") from err
