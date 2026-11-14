"""Tell the user once about each event code the integration does not know yet.

The notification asks for the matching app message and links to a pre-filled GitHub issue, so new codes can be
added to `event_codes.py`. Each code is reported only once per Home Assistant installation (kept in `.storage`).
It can be turned off in the integration options.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_NOTIFY_UNKNOWN_EVENT_CODES,
    DEFAULT_NOTIFY_UNKNOWN_EVENT_CODES,
    DOMAIN,
)
from .coordinator import HandwiseGenieDataUpdateCoordinator
from .event_codes import (
    build_issue_url,
    format_firmware,
    is_reportable_event_code,
    normalize_event_code,
    notification_texts,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{DOMAIN}.unknown_event_codes"
STORAGE_VERSION = 1
DATA_NOTIFIED_CODES = f"{DOMAIN}_notified_event_codes"


class NotifiedEventCodes:
    """Event codes the user was already told about (shared by all config entries)."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.codes: set[int] = set()
        self.load_task: asyncio.Task[None] | None = None

    async def async_load(self) -> None:
        """Load the codes from storage."""
        data = await self._store.async_load()
        codes = data.get("codes") if isinstance(data, dict) else None
        if isinstance(codes, list):
            self.codes = {
                code
                for code in (normalize_event_code(item) for item in codes)
                if code is not None
            }

    @callback
    def async_add(self, code: int) -> None:
        """Remember a code and save it soon."""
        self.codes.add(code)
        self._store.async_delay_save(lambda: {"codes": sorted(self.codes)}, 1)


async def async_get_notified_event_codes(hass: HomeAssistant) -> NotifiedEventCodes:
    """Return the shared list of reported codes, loaded once."""
    notified: NotifiedEventCodes | None = hass.data.get(DATA_NOTIFIED_CODES)
    if notified is None:
        notified = NotifiedEventCodes(hass)
        hass.data[DATA_NOTIFIED_CODES] = notified
        notified.load_task = hass.async_create_task(notified.async_load())
    if notified.load_task is not None:
        try:
            await notified.load_task
        except Exception:
            # Let the next setup attempt create a fresh tracker and read the file again.
            if hass.data.get(DATA_NOTIFIED_CODES) is notified:
                hass.data.pop(DATA_NOTIFIED_CODES)
            raise
    return notified


def _format_local_time(value: datetime) -> tuple[str, str]:
    """Return ('2026-11-14 18:03', '2026-11-14 18:03 (UTC+01:00)') in local time."""
    local = dt_util.as_local(value)
    short = local.strftime("%Y-%m-%d %H:%M")
    offset = local.strftime("%z")
    if len(offset) == 5:
        offset = f"{offset[:3]}:{offset[3:]}"
    return short, f"{short} (UTC{offset})"


class UnknownEventCodeWatcher:
    """Watch the `event_code` of one mower and notify about unknown values."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        coordinator: HandwiseGenieDataUpdateCoordinator,
        notified: NotifiedEventCodes,
        integration_version: str,
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._coordinator = coordinator
        self._notified = notified
        self._integration_version = integration_version
        self._current_code: int | None = None
        self._previous_code: int | None = None
        self._changed_at: datetime | None = None
        self._mode_at_change: Any = None

    @callback
    def async_check(self) -> None:
        """Check the latest reported state (coordinator listener)."""
        if not self._coordinator.last_update_success:
            return
        state = self._coordinator.reported_state
        code = normalize_event_code(state.get("event_code"))
        if code is None:
            return
        if code != self._current_code:
            self._previous_code = self._current_code
            self._current_code = code
            self._changed_at = dt_util.now()
            self._mode_at_change = state.get("mode")

        if not is_reportable_event_code(code) or code in self._notified.codes:
            return
        if not self._entry.options.get(
            CONF_NOTIFY_UNKNOWN_EVENT_CODES, DEFAULT_NOTIFY_UNKNOWN_EVENT_CODES
        ):
            return
        self._notify(code, state)

    @callback
    def _notify(self, code: int, state: dict[str, Any]) -> None:
        device = self._coordinator.device
        short_time, seen_at = _format_local_time(self._changed_at or dt_util.now())
        mode = self._mode_at_change if self._changed_at else state.get("mode")
        issue_url = build_issue_url(
            code=code,
            previous_code=self._previous_code,
            seen_at=seen_at,
            mode=mode,
            model=device.model,
            firmware=format_firmware(state.get("fw_version")),
            integration_version=self._integration_version,
            ha_version=HA_VERSION,
        )
        title, message = notification_texts(
            self._hass.config.language,
            name=device.alias or device.model or "MGC",
            code=code,
            time=short_time,
            issue_url=issue_url,
        )
        persistent_notification.async_create(
            self._hass,
            message,
            title=title,
            notification_id=f"{DOMAIN}_unknown_event_code_{code}",
        )
        _LOGGER.warning(
            "Unknown event_code %s (previous %s, mode %s). Please report it: %s",
            code,
            self._previous_code,
            mode,
            issue_url,
        )
        self._notified.async_add(code)
