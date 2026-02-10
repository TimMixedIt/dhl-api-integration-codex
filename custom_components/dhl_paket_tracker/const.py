"""Constants for the DHL Paket Tracker integration."""

from datetime import timedelta

DOMAIN = "dhl_paket_tracker"
PLATFORMS = ["sensor"]

CONF_API_KEY = "api_key"
CONF_TRACKING_NUMBERS = "tracking_numbers"
CONF_POLL_INTERVAL_MINUTES = "poll_interval_minutes"

DEFAULT_POLL_INTERVAL_MINUTES = 30
DEFAULT_SCAN_INTERVAL = timedelta(minutes=DEFAULT_POLL_INTERVAL_MINUTES)

API_BASE_URL = "https://api-eu.dhl.com/track/shipments"
ATTR_TRACKING_NUMBER = "tracking_number"
ATTR_SERVICE = "service"
ATTR_ORIGIN = "origin"
ATTR_DESTINATION = "destination"
ATTR_EVENTS = "events"
ATTR_ESTIMATED_DELIVERY = "estimated_delivery"
ATTR_STATUS_CODE = "status_code"
ATTR_STATUS_DESCRIPTION = "status_description"
