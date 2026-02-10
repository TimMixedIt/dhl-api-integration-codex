"""The DHL Paket Tracker integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_TRACKING_NUMBERS,
)
from .coordinator import DhlPaketCoordinator
from .dhl_api import DHLApiClient

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass(slots=True)
class DhlPaketRuntimeData:
    """Runtime data for a config entry."""

    coordinator: DhlPaketCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DHL Paket Tracker from a config entry."""
    session = async_get_clientsession(hass)
    client = DHLApiClient(
        api_key=entry.data[CONF_API_KEY],
        api_secret=entry.data.get(CONF_API_SECRET),
        session=session,
    )

    coordinator = DhlPaketCoordinator(
        hass,
        client=client,
        tracking_numbers=entry.data[CONF_TRACKING_NUMBERS],
        poll_interval_minutes=entry.data[CONF_POLL_INTERVAL_MINUTES],
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = DhlPaketRuntimeData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
