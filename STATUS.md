# STATUS

Read this first, and update it after every step, so the next session can continue without the chat history.

Last updated: 2026-11-14 (PR #14 merged, 0.2.2 not released yet)

## Current state

- **0.2.1** (HACS) on the maintainer's device (Redkey MGC1000), plus the debug patch `extras/shadow_capture`.
- **0.2.2 on `main` since 2026-11-14** (PR #14 merged with the CodeRabbit fix: the answer window of the status request is timed with a monotonic clock from when it was sent). No GitHub release yet, so HACS does not offer it. Connection = `online` and not `shutdown` and the mower answers; one `get_all_props` request when the last report is older than 6 h.
- **On the device:** files of PR #14 applied by hand on 2026-11-11, active since a later HA restart; checked 2026-11-14: attribute `last_report` present, sensor on while docked. The CodeRabbit fix (`coordinator.py`) is copied, active only after the next HA restart. **Not checked yet:** mower off → disconnected at `shutdown`; without power → after 6 h; on → connected again.
- **Event codes:** meaning of `event_code` collected from the app Message Center, see `extras/event_codes/` (2026-11-12). Code 3 still unknown.

## Next steps

1. Test 0.2.2 on the device (mower off → disconnected at `shutdown`; without power → after 6 h; on → connected again), then publish the 0.2.2 release (only when the maintainer asks).
2. Show `event_code` as text in HA (sensor or attribute, table from `extras/event_codes/`), e.g. code 41 = rain.
3. Port 7789 on the mower sends a binary stream (header `AA AA`) without request. Record it read-only while the mower changes state and compare with the shadow – maybe a local status without cloud.

## Known issues and backlog

- Cloud login only at start; the bearer token is valid 360 h (15 days). After that, fetching IoT credentials fails until a reload.
- Sensors are only created if their field exists at the first fetch; a failed first shadow fetch leaves them missing until a restart.
- Static signing fallback in `api.py` uses undefined constants (`NameError` instead of a clear message).
- `lawn_mower`: `idle`, `sleep`, `shutdown` count as docked; ERROR is never reported.
- Polling every 240 s: short `event_code` changes (several messages within seconds) are missed.
- Some entities have no German translation; no `translations/en.json`.
- Message centre list (`device/v2/code/list`) stays empty for the MGC.

## Decisions and conventions

- Fork of `MTTPoll/handwise-ha`; our `main` sets the version. Rules for branches, commits and PRs: `CLAUDE.md`.
- Only `ctl_rainer`, `mow_delay` and `mow_regular` are written to the mower without asking; everything else (especially `ota_start`) only with explicit approval.
- Rain wait time is sent as `mow_delay` in minutes (0–12 h); the app only offers 1–3 h and overwrites the value if changed there.
- Documentation-only changes get no new version.

## Key files

- `custom_components/mgc_mower/api.py` – cloud login, AWS IoT shadow, commands
- `custom_components/mgc_mower/coordinator.py` – polling (240 s)
- `custom_components/mgc_mower/sensor.py`, `binary_sensor.py`, `lawn_mower.py` – entities
- `extras/shadow_capture/` – debug patch (`mgc_mower.capture_shadow`), not installed by HACS
- `extras/dashboard/` – example dashboard with weekly schedule editor
- `extras/event_codes/` – event code table, how-to, app screenshots
