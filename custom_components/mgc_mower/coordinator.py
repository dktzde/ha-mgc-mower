"""Data coordinator for Handwise MGC01."""

from __future__ import annotations

from datetime import timedelta
import logging
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
# report is older than this, it is asked for its status ("get_all_props").
STALE_REPORT_SECONDS = 1800
# A status request is judged at the first poll that is at least this much later.
# An online mower answers within a few seconds.
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
        self._probe_shadow_time: int | None = None
        self._device_responding = True

    @property
    def reported_state(self) -> dict[str, Any]:
        """Return the latest reported state."""
        return self.data if isinstance(self.data, dict) else {}

    def _judge_report_age(self) -> bool:
        """Update the responding flag; return true if a status request is due."""
        shadow_time = self.client.property_shadow_time
        report_time = self.client.property_report_time
        if shadow_time is None or report_time is None:
            return False
        if shadow_time - report_time <= STALE_REPORT_SECONDS:
            self._probe_shadow_time = None
            self._device_responding = True
            return False
        if self._probe_shadow_time is None:
            return True
        if shadow_time - self._probe_shadow_time < PROBE_ANSWER_SECONDS:
            # Too early to judge, e.g. a refresh right after a command.
            return False
        # Still stale although a status request was sent: the mower is not reachable.
        # (An answer would have made the report fresh, see above.)
        self._device_responding = False
        self._probe_shadow_time = None
        return True

    async def _async_probe_if_stale(self) -> None:
        """Ask a silent mower for its status so the next poll can tell if it is online."""
        if not self.client.supports_status_probe:
            return
        if not self._judge_report_age():
            return
        try:
            await self.client.async_request_all_properties()
        except HandwiseGenieApiError as err:
            _LOGGER.debug("Status request to a silent mower failed: %s", err)
            return
        self._probe_shadow_time = self.client.property_shadow_time

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest state from the cloud endpoint."""
        try:
            await self.client.async_ensure_temporary_credentials(self.account_client)
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

            await self._async_probe_if_stale()

            merged_state = dict(property_state)
            merged_state["_device_responding"] = self._device_responding
            merged_state["_last_report_time"] = self.client.property_report_time
            merged_state["_service_reported"] = service_state
            merged_state["_area_definition"] = self._area_definition
            return merged_state
        except HandwiseGenieApiError as err:
            raise UpdateFailed(str(err)) from err
