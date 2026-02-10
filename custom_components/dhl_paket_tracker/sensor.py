"""Sensor platform for DHL Paket Tracker."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DhlPaketRuntimeData
from .const import (
    ATTR_DESTINATION,
    ATTR_ESTIMATED_DELIVERY,
    ATTR_EVENTS,
    ATTR_ORIGIN,
    ATTR_SERVICE,
    ATTR_STATUS_CODE,
    ATTR_STATUS_DESCRIPTION,
    ATTR_TRACKING_NUMBER,
    CONF_TRACKING_NUMBERS,
    DOMAIN,
)
from .coordinator import DhlPaketCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DHL tracking sensors based on a config entry."""
    runtime_data: DhlPaketRuntimeData = entry.runtime_data
    coordinator = runtime_data.coordinator

    entities = [
        DhlShipmentSensor(coordinator=coordinator, tracking_number=tracking_number)
        for tracking_number in entry.data[CONF_TRACKING_NUMBERS]
    ]
    async_add_entities(entities)


class DhlShipmentSensor(CoordinatorEntity[DhlPaketCoordinator], SensorEntity):
    """Representation of a DHL tracked shipment."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:package-variant"

    def __init__(self, coordinator: DhlPaketCoordinator, tracking_number: str) -> None:
        super().__init__(coordinator)
        self._tracking_number = tracking_number
        self._attr_name = f"Sendung {tracking_number[-6:]}"
        self._attr_unique_id = f"{DOMAIN}_{tracking_number}"

    @property
    def native_value(self) -> str | None:
        """Return the sensor state (shipment status)."""
        shipment = self.coordinator.data.get(self._tracking_number, {})
        status = shipment.get("status", {})
        return status.get("status") or status.get("description")

    @property
    def extra_state_attributes(self) -> dict:
        """Return shipment details as attributes."""
        shipment = self.coordinator.data.get(self._tracking_number, {})
        status = shipment.get("status", {})
        events = shipment.get("events", [])

        origin = shipment.get("origin", {}).get("address", {})
        destination = shipment.get("destination", {}).get("address", {})

        return {
            ATTR_TRACKING_NUMBER: self._tracking_number,
            ATTR_STATUS_CODE: status.get("status"),
            ATTR_STATUS_DESCRIPTION: status.get("description"),
            ATTR_SERVICE: shipment.get("service"),
            ATTR_ESTIMATED_DELIVERY: shipment.get("estimatedTimeOfDelivery"),
            ATTR_ORIGIN: ", ".join(
                part for part in [origin.get("addressLocality"), origin.get("countryCode")] if part
            )
            or None,
            ATTR_DESTINATION: ", ".join(
                part
                for part in [
                    destination.get("addressLocality"),
                    destination.get("countryCode"),
                ]
                if part
            )
            or None,
            ATTR_EVENTS: [
                {
                    "timestamp": event.get("timestamp"),
                    "description": event.get("description"),
                    "status": event.get("status"),
                    "location": event.get("location", {}).get("address", {}).get(
                        "addressLocality"
                    ),
                }
                for event in events[:10]
            ],
        }
