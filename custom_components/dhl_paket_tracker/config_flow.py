"""Config flow for DHL Paket Tracker."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_TRACKING_NUMBERS,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
)
from .dhl_api import DHLApiAuthError, DHLApiClient, DHLApiError


class DhlPaketTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DHL Paket Tracker."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow state."""
        self._auth_input: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Step 1: ask for credentials first (always includes secret field)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            api_secret = user_input.get(CONF_API_SECRET, "").strip() or None
            poll_interval = user_input[CONF_POLL_INTERVAL_MINUTES]

            if not api_key:
                errors["base"] = "invalid_auth"
            else:
                self._auth_input = {
                    CONF_API_KEY: api_key,
                    CONF_API_SECRET: api_secret,
                    CONF_POLL_INTERVAL_MINUTES: poll_interval,
                }
                return await self.async_step_tracking()

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_API_SECRET): str,
                vol.Optional(
                    CONF_POLL_INTERVAL_MINUTES,
                    default=DEFAULT_POLL_INTERVAL_MINUTES,
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=720)),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_tracking(self, user_input: dict[str, Any] | None = None):
        """Step 2: ask for tracking numbers and validate with configured credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            raw_numbers = user_input[CONF_TRACKING_NUMBERS]
            tracking_numbers = [
                num.strip() for num in raw_numbers.replace("\n", ",").split(",") if num.strip()
            ]

            if not tracking_numbers:
                errors["base"] = "missing_tracking_numbers"
            else:
                session = async_get_clientsession(self.hass)
                client = DHLApiClient(
                    api_key=self._auth_input[CONF_API_KEY],
                    api_secret=self._auth_input.get(CONF_API_SECRET),
                    session=session,
                )

                try:
                    await client.async_get_shipment(tracking_numbers[0])
                except DHLApiAuthError:
                    errors["base"] = "invalid_auth"
                except DHLApiError:
                    # Do not block setup for all non-auth API errors because
                    # response codes can depend on shipment visibility/product.
                    pass
                except Exception:  # pylint: disable=broad-except
                    errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{'_'.join(sorted(tracking_numbers))}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"DHL ({len(tracking_numbers)} Sendungen)",
                    data={
                        CONF_API_KEY: self._auth_input[CONF_API_KEY],
                        CONF_API_SECRET: self._auth_input.get(CONF_API_SECRET),
                        CONF_TRACKING_NUMBERS: tracking_numbers,
                        CONF_POLL_INTERVAL_MINUTES: self._auth_input[
                            CONF_POLL_INTERVAL_MINUTES
                        ],
                    },
                )

        schema = vol.Schema({vol.Required(CONF_TRACKING_NUMBERS): str})
        return self.async_show_form(step_id="tracking", data_schema=schema, errors=errors)
