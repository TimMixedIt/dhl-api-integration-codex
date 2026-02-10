"""Async DHL Paket tracking API client."""

from __future__ import annotations

from dataclasses import dataclass

import aiohttp

from .const import API_BASE_URL


class DHLApiError(Exception):
    """Base API exception."""


class DHLApiAuthError(DHLApiError):
    """Authentication with the DHL API failed."""


@dataclass(slots=True)
class TrackingResult:
    """Normalized shipment payload."""

    tracking_number: str
    raw: dict


class DHLApiClient:
    """Client for DHL shipment tracking endpoints."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._session = session

    async def async_get_shipment(self, tracking_number: str) -> TrackingResult:
        """Fetch a single shipment by tracking number."""
        headers = {
            "Accept": "application/json",
            "DHL-API-Key": self._api_key,
            "User-Agent": "HomeAssistantDhlPaketTracker/0.1",
        }
        params = {"trackingNumber": tracking_number}

        async with self._session.get(
            API_BASE_URL,
            headers=headers,
            params=params,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:
            if response.status == 401:
                raise DHLApiAuthError("Authentication failed. Please check your DHL API key.")

            if response.status >= 400:
                text = await response.text()
                raise DHLApiError(
                    f"DHL API request failed for {tracking_number}: {response.status} {text}"
                )

            payload = await response.json()

        shipments = payload.get("shipments") or []
        if not shipments:
            raise DHLApiError(
                f"No shipment data returned for tracking number {tracking_number}."
            )

        return TrackingResult(tracking_number=tracking_number, raw=shipments[0])
