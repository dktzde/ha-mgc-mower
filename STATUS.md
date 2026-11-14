# STATUS

Read this first, and update it after every step, so the next session can continue without the chat history.

Last updated: 2026-11-14 (0.3.0: unknown event code notifications, translations)

## Current state

- **0.2.2** published 2026-11-14 18:55 (CET): connection = `online` and not `shutdown` and the mower answers; one `get_all_props` request when the last report is older than 6 h.
- **0.3.0** (branch `feat/unknown-event-code-notice`): unknown `event_code` → one Home Assistant notification per code with a pre-filled issue link (form `.github/ISSUE_TEMPLATE/unknown_event_code.yml`, label `event code`); option to turn it off (on by default); attributes `description` and `known` on the event code sensor; translations en/de/fr (entities, options, services); example dashboard and schedule package in German and French.
- **On the device (Redkey MGC1000):** branch code + debug patch `extras/shadow_capture` installed by hand, HA restarted 2026-11-14 19:09. **Checked 2026-11-14 19:12–19:20:** notification appears once (German, link with code, mode, model, firmware, versions; no serial number), log warning, codes kept in `.storage/mgc_mower.unknown_event_codes`, options flow off/on saved without reload, translations loaded (de/en/fr), all 33 entities available, `capture_shadow` still registered. For the test, code 244 was taken out of the table locally. **Not checked yet:** a real unknown code while the option is off (covered by an offline test with stubbed Home Assistant modules); the pre-filled issue form (needs the template on `main`).
- PR #14 parts on the device since 2026-11-14 19:09. **Not checked yet:** mower off → disconnected at `shutdown`; without power → after 6 h; on → connected again.
- **Event codes:** meaning of `event_code` collected from the app Message Center, see `extras/event_codes/` (2026-11-12). Code 3 still unknown.

## Next steps

1. After the merge: GitHub pre-release v0.3.0, install it from HACS (re-apply `extras/shadow_capture`), restart, check that 244 is known again and the issue link opens the filled-in form.
2. Test PR #14 on the device (mower off / without power / on).
3. Port 7789 on the mower sends a binary stream (header `AA AA`) without request. Record it read-only while the mower changes state and compare with the shadow – maybe a local status without cloud.

## Known issues and backlog

- Cloud login only at start; the bearer token is valid 360 h (15 days). After that, fetching IoT credentials fails until a reload.
- Sensors are only created if their field exists at the first fetch; a failed first shadow fetch leaves them missing until a restart.
- Static signing fallback in `api.py` uses undefined constants (`NameError` instead of a clear message).
- `lawn_mower`: `idle`, `sleep`, `shutdown` count as docked; ERROR is never reported.
- Polling every 240 s: short `event_code` changes (several messages within seconds) are missed.
- Existing installations keep their entity IDs when translations change; the German/French example dashboards use the IDs of a fresh install.
- Message centre list (`device/v2/code/list`) stays empty for the MGC.

## Decisions and conventions

- Fork of `MTTPoll/handwise-ha`; our `main` sets the version. Rules for branches, commits and PRs: `CLAUDE.md`.
- Only `ctl_rainer`, `mow_delay` and `mow_regular` are written to the mower without asking; everything else (especially `ota_start`) only with explicit approval.
- Rain wait time is sent as `mow_delay` in minutes (0–12 h); the app only offers 1–3 h and overwrites the value if changed there.
- Documentation-only changes get no new version.
- Unknown event codes: notify once per code and installation; `0` and empty values are never reported; the issue link carries no serial number, IP address or account data. English translation names equal the code's `name=` values, so English entity IDs stay the same.
- New event codes: add them to `KNOWN_EVENT_CODES` in `event_codes.py` and to the table in `extras/event_codes/README.md`.

## Key files

- `custom_components/mgc_mower/api.py` – cloud login, AWS IoT shadow, commands
- `custom_components/mgc_mower/coordinator.py` – polling (240 s)
- `custom_components/mgc_mower/sensor.py`, `binary_sensor.py`, `lawn_mower.py` – entities
- `custom_components/mgc_mower/event_codes.py` – known event codes, issue link, notification texts (no HA imports)
- `custom_components/mgc_mower/event_notice.py` – watches `event_code`, notification, storage
- `custom_components/mgc_mower/translations/` – en, de, fr (`strings.json` = en)
- `extras/shadow_capture/` – debug patch (`mgc_mower.capture_shadow`), not installed by HACS
- `extras/dashboard/` – example dashboard with weekly schedule editor (en, de, fr)
- `extras/event_codes/` – event code table, how-to, app screenshots
