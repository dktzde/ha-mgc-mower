# Shadow capture (debug extra)

Developer tool for finding out how the mower is controlled. **Not part of the integration**: HACS only installs `custom_components/mgc_mower`, so this patch has to be applied by hand and is lost again with every update.

The mower talks to the cloud through two AWS IoT "shadows" (`property` and `service`). The vendor app (R HOME, Handwise, Anthbot) sends commands by writing `desired` into the `service` shadow, and the mower answers in `reported`. This patch makes that traffic visible, which is how the rain commands (`ctl_rainer`, `mow_delay`) and the weekly schedule (`mow_regular`) of 0.2.0 were worked out.

## What the patch adds

| File | Change |
|------|--------|
| `__init__.py` | Service `mgc_mower.capture_shadow` (`duration` 5–1800 s, default 300; `interval` 0.2–10 s, default 0.5). Polls both shadows in a background task and logs every new version as **WARNING** lines starting with `CAPTURE`: shadow version, `desired`, `delta`, rain settings (`rainer_ctl`, `mow_delay_time`), schedule (`appointment`, `appointment_time`), cutting height and direction. At the start it logs all field names of the `property` shadow once. |
| `api.py` | Keeps the last raw shadow document per shadow (`_last_shadow_payload`, used by the service) and logs the complete `service` shadow at **debug** level. |
| `services.yaml` | Description of `capture_shadow` for the UI. |

Everything is **read-only**: nothing is sent to the mower. Polling every 0.5 s means more cloud requests for the duration of the capture, so keep it short.

## Install

In the Home Assistant configuration folder (the one with `custom_components/`):

```sh
patch -p1 < shadow_capture.patch
```

Then restart Home Assistant. Remove it again with `patch -R -p1 < shadow_capture.patch` (or just update / reinstall the integration). The patch is made against the version in this repository; after an update apply it again, and if it no longer applies, compare by hand.

## Use

1. Developer tools → Actions → `mgc_mower.capture_shadow`, pick the mower, e.g. `duration: 300`.
2. Within those 5 minutes change the setting in the vendor app.
3. Read the `CAPTURE` lines in the log (Settings → System → Logs, or `ha core logs | grep CAPTURE`). The `desired` part of the `service` shadow is the command the app sent.

For the full `service` document on every poll, also enable debug logging:

```yaml
logger:
  logs:
    custom_components.mgc_mower.api: debug
```

---

## Deutsch (kurz)

Entwickler-Werkzeug, **nicht Teil der Integration**: von Hand einspielen (`patch -p1 < shadow_capture.patch` im HA-Konfigordner, dann HA neu starten), ein Update überschreibt es. Der Dienst `mgc_mower.capture_shadow` liest die beiden Shadows des Mähers schnell hintereinander und schreibt jede Änderung als WARNING-Zeile `CAPTURE` ins Log, inklusive `desired` = Befehl der Hersteller-App. Während der Aufnahme die Einstellung in der App ändern, dann die Zeilen lesen. `api.py` merkt sich dafür das letzte Shadow-Dokument und loggt den ganzen `service`-Shadow auf Debug-Ebene. Nur lesend, es wird nichts an den Mäher geschickt.
