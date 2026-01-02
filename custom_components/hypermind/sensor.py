"""Sensor platform for Hypermind."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HypermindDataUpdateCoordinator
from .const import (
    DOMAIN,
    ATTR_ACTIVE_NODES,
    ATTR_DIRECT_CONNECTIONS,
    ATTR_SCALE_MIN,
    ATTR_SCALE_MAX,
    ATTR_SCALE_RATIO,
)

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_ACTIVE_NODES,
        name="Active Nodes",
        icon="mdi:server-network",
        native_unit_of_measurement="nodes",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_DIRECT_CONNECTIONS,
        name="Direct Connections",
        icon="mdi:connection",
        native_unit_of_measurement="connections",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hypermind sensor based on a config entry."""
    coordinator: HypermindDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities(
        HypermindSensor(coordinator, description, entry)
        for description in SENSOR_DESCRIPTIONS
    )


class HypermindSensor(CoordinatorEntity[HypermindDataUpdateCoordinator], SensorEntity):
    """Representation of a Hypermind sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HypermindDataUpdateCoordinator,
        description: SensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Hypermind",
            "manufacturer": "lklynet",
            "model": "Hypermind P2P Counter",
            "sw_version": "1.0.0",
            "configuration_url": f"http://{coordinator.host}:{coordinator.port}",
        }

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return additional attributes for the Active Nodes sensor."""
        if self.coordinator.data is None:
            return None
        
        # Only add scale attributes to the Active Nodes sensor
        if self.entity_description.key == ATTR_ACTIVE_NODES:
            return {
                ATTR_SCALE_MIN: self.coordinator.data.get("scale_min"),
                ATTR_SCALE_MAX: self.coordinator.data.get("scale_max"),
                ATTR_SCALE_RATIO: self.coordinator.data.get("scale_ratio"),
            }
        return None
