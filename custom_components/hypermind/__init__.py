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
    CONF_SCALE_MIN,
    CONF_SCALE_MAX,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SCALE_MIN,
    DEFAULT_SCALE_MAX,
    ATTR_ACTIVE_NODES,
    ATTR_DIRECT_CONNECTIONS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hypermind from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    
    # Get scale values from options first, then data, then defaults
    scale_min = entry.options.get(
        CONF_SCALE_MIN,
        entry.data.get(CONF_SCALE_MIN, DEFAULT_SCALE_MIN)
    )
    scale_max = entry.options.get(
        CONF_SCALE_MAX,
        entry.data.get(CONF_SCALE_MAX, DEFAULT_SCALE_MAX)
    )
    
    coordinator = HypermindDataUpdateCoordinator(
        hass, host, port, scale_min, scale_max
    )
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register listener for options updates
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class HypermindDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Hypermind data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        scale_min: int,
        scale_max: int,
    ) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.scale_min = scale_min
        self.scale_max = scale_max
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
                        
                        active_nodes = data.get("count", 0)
                        
                        # Calculate normalized ratio (0.0 to 1.0)
                        scale_range = self.scale_max - self.scale_min
                        if scale_range > 0:
                            clamped = max(self.scale_min, min(active_nodes, self.scale_max))
                            ratio = (clamped - self.scale_min) / scale_range
                        else:
                            ratio = 0.0
                        
                        return {
                            ATTR_ACTIVE_NODES: active_nodes,
                            ATTR_DIRECT_CONNECTIONS: data.get("direct", 0),
                            "scale_min": self.scale_min,
                            "scale_max": self.scale_max,
                            "scale_ratio": round(ratio, 4),
                        }
                    raise UpdateFailed(f"API returned status {response.status}")
                    
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Hypermind: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with Hypermind: {err}") from err
