"""Config flow for DHL Paket Tracker."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_TRACKING_NUMBERS,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
)
from .dhl_api import DHLApiAuthError, DHLApiClient, DHLApiError


class DhlPaketTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DHL Paket Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            raw_numbers = user_input[CONF_TRACKING_NUMBERS]
            tracking_numbers = [
                num.strip() for num in raw_numbers.replace("\n", ",").split(",") if num.strip()
            ]

            if not tracking_numbers:
                errors["base"] = "missing_tracking_numbers"
            else:
                session = async_get_clientsession(self.hass)
                client = DHLApiClient(api_key=api_key, session=session)

                try:
                    await client.async_get_shipment(tracking_numbers[0])
                except DHLApiAuthError:
                    errors["base"] = "invalid_auth"
                except DHLApiError:
                    errors["base"] = "cannot_connect"
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
                        CONF_API_KEY: api_key,
                        CONF_TRACKING_NUMBERS: tracking_numbers,
                        CONF_POLL_INTERVAL_MINUTES: user_input[
                            CONF_POLL_INTERVAL_MINUTES
                        ],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_TRACKING_NUMBERS): str,
                vol.Optional(
                    CONF_POLL_INTERVAL_MINUTES,
                    default=DEFAULT_POLL_INTERVAL_MINUTES,
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=720)),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
