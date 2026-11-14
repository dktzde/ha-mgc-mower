"""Data coordinator for Handwise MGC01."""

from __future__ import annotations

from datetime import timedelta
import logging
import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    HandwiseBoundDevice,
    HandwiseCloudApiClient,
    HandwiseGenieApiError,
    HandwiseShadowApiClient,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# The shadow keeps the last values forever, also "online": 1 after the mower lost
# power or Wi-Fi. A docked mower does not report on its own, so when its last
# report is older than this, it is asked once for its status ("get_all_props").
# Without an answer it counts as off and is not asked again; it reports on its
# own when it is back (e.g. "charging").
STALE_REPORT_SECONDS = 6 * 3600
# A status request is judged at the first poll whose shadow fetch starts at least
# this many seconds after the request was sent. An online mower answers within a
# few seconds.
PROBE_ANSWER_SECONDS = 20


class HandwiseGenieDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch and cache Handwise shadow state."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        account_client: HandwiseCloudApiClient,
        client: HandwiseShadowApiClient,
        device: HandwiseBoundDevice,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.account_client = account_client
        self.client = client
        self.device = device
        self._area_definition: dict[str, Any] = {}
        self._last_area_time: str | None = None
        # Monotonic time when the last status request was sent.
        self._probe_sent: float | None = None
        self._device_responding = True

    @property
    def reported_state(self) -> dict[str, Any]:
        """Return the latest reported state."""
        return self.data if isinstance(self.data, dict) else {}

    def _judge_report_age(self, fetch_started: float, mode: Any = None) -> bool:
        """Update the responding flag; return true if a status request is due.

        `fetch_started` is the monotonic time at which this poll's shadow fetch
        started. Cloud timestamps are only used for the report age.
        """
        shadow_time = self.client.property_shadow_time
        report_time = self.client.property_report_time
        if shadow_time is None or report_time is None:
            return False
        if shadow_time - report_time <= STALE_REPORT_SECONDS:
            self._probe_sent = None
            self._device_responding = True
            return False
        if not self._device_responding:
            # Already counted as off: wait for the mower to report on its own.
            return False
        if self._probe_sent is None:
            # A mower that reported "shutdown" is off anyway, no need to ask.
            return not (isinstance(mode, str) and mode.lower() == "shutdown")
        if fetch_started - self._probe_sent < PROBE_ANSWER_SECONDS:
            # Too early to judge, e.g. a refresh right after a command.
            return False
        # Still stale although a status request was sent: the mower is not reachable.
        # (An answer would have made the report fresh, see above.)
        self._device_responding = False
        self._probe_sent = None
        return False

    async def _async_probe_if_stale(
        self, fetch_started: float, mode: Any = None
    ) -> None:
        """Ask a silent mower for its status so the next poll can tell if it is online."""
        if not self.client.supports_status_probe:
            return
        if not self._judge_report_age(fetch_started, mode):
            return
        try:
            await self.client.async_request_all_properties()
        except HandwiseGenieApiError as err:
            _LOGGER.debug("Status request to a silent mower failed: %s", err)
            return
        self._probe_sent = time.monotonic()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest state from the cloud endpoint."""
        try:
            await self.client.async_ensure_temporary_credentials(self.account_client)
            fetch_started = time.monotonic()
            property_state = await self.client.async_get_shadow_reported_state()
            _LOGGER.debug("ANTHBOT PROPERTY STATE: %s", property_state)
            try:
                service_state = await self.client.async_get_service_reported_state()
                _LOGGER.debug("ANTHBOT SERVICE STATE: %s", service_state)
            except HandwiseGenieApiError:
                service_state = {}

            area_time = property_state.get("area_time")
            if not isinstance(area_time, str):
                area_time = None
            should_refresh_area = not self._area_definition or (
                area_time is not None and area_time != self._last_area_time
            )
            if should_refresh_area:
                try:
                    self._area_definition = (
                        await self.account_client.async_get_device_area_definition(
                            self.client.serial_number
                        )
                    )
                    self._last_area_time = area_time
                except HandwiseGenieApiError:
                    if not self._area_definition:
                        self._area_definition = {}

            await self._async_probe_if_stale(
                fetch_started, property_state.get("mode")
            )

            merged_state = dict(property_state)
            merged_state["_device_responding"] = self._device_responding
            merged_state["_last_report_time"] = self.client.property_report_time
            merged_state["_service_reported"] = service_state
            merged_state["_area_definition"] = self._area_definition
            return merged_state
        except HandwiseGenieApiError as err:
            raise UpdateFailed(str(err)) from err
