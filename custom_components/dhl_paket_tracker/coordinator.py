"""Data update coordinator for DHL Paket Tracker."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .dhl_api import DHLApiAuthError, DHLApiClient, DHLApiError

_LOGGER = logging.getLogger(__name__)


class DhlPaketCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Fetch DHL shipment data for all configured tracking numbers."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        client: DHLApiClient,
        tracking_numbers: list[str],
        poll_interval_minutes: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="DHL Paket Tracker",
            update_interval=timedelta(minutes=poll_interval_minutes),
        )
        self.client = client
        self.tracking_numbers = tracking_numbers

    async def _async_update_data(self) -> dict[str, dict]:
        data: dict[str, dict] = {}
        for number in self.tracking_numbers:
            try:
                result = await self.client.async_get_shipment(number)
                data[number] = result.raw
            except DHLApiAuthError as err:
                raise ConfigEntryAuthFailed(str(err)) from err
            except DHLApiError as err:
                raise UpdateFailed(str(err)) from err
            except Exception as err:  # pylint: disable=broad-except
                raise UpdateFailed(f"Unexpected error for {number}: {err}") from err

        return data
