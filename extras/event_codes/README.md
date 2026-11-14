# MGC `event_code` – meaning of the values

The mower writes `event_code` into its AWS IoT shadow (`property/reported`). The R HOME app shows each change as a
text in the **Message Center**. The cloud list `device/v2/code/list` stays empty for the MGC, and the code table
(`message/code/translate`, codes 1000–2155) does not cover these values. No other project (ioBroker anthbot adapters,
ha-anthbot-map-v2, handwise-ha) maps them – they only show the raw number.

Entity in this integration: `sensor.<name>_event_code` (diagnostic). Since 0.3.0 its attribute `description` shows the app text below and `known` tells whether the code is in the table (`custom_components/mgc_mower/event_codes.py`).

## Known values (Redkey MGC1000, firmware ui_board 0.3.5)

| `event_code` | App text (Message Center) | Evidence (local time) | Sure? |
|---|---|---|---|
| 4 | Device is shutdown | 2026-11-10 21:02:59 | yes |
| 18 | Device is fully charged | 2026-11-04, 11-06, 11-11 | yes |
| 23 | Device is charging | 2026-11-04, 11-06, 11-11 | yes |
| 41 | It's raining, can't mowing. | 2026-11-12 00:30:50 | yes |
| 63 | Mowing is finished (same second: "Device is back to the dock", "Device is charging") | 2026-11-04 15:01:45 | likely |
| 66 | Plan's mowing is on | 2026-11-04 13:59:59 | yes |
| 235 | Battery temperature too high while charging, charging paused | 2026-11-06 07:59, 08:53; 11-07 01:46 | yes |
| 236 | The temperature has returned to normal, continue charging. | 2026-11-06 12:29; 11-07 12:15 | yes |
| 244 | The PIN code is not unlocked, so this scheduled task cannot be executed. | 2026-11-11 13:59:44 | yes |
| 253 | Stop key had been trigger, so this scheduled task cannot be executed. | 2026-11-07 13:59:55 | yes |
| 3 | unknown | 2026-10-29 | – |

Seen in the app but not yet caught as a code (several events within seconds; HA polls every 240 s and only sees the
last one): "Device is paused", "Mower is not started on the dock or boundary wire", "Device goes on back to the dock",
"Device is back to the dock", "0".

## How to read your own codes (repro)

1. Keep the history of `sensor.<name>_event_code` (recorder default: 10 days).
2. In the R HOME app tap the speech-bubble icon top right on the start screen (`screenshots/01_…`) → **Message Center**.
3. Screenshot the list (`screenshots/02…04`). App times are local time.
4. Match each app message with a change of `event_code` in the HA history: the change appears 0–4 min **after** the
   app time (polling interval 240 s). Several messages within a few seconds → only the last one is visible.
5. Please report new values with the issue form [Unknown event code](https://github.com/dktzde/ha-mgc-mower/issues/new?template=unknown_event_code.yml). Since 0.3.0 Home Assistant also shows a notification with a pre-filled link when the mower reports an unknown code (can be turned off in the integration options).

Screenshots: R HOME app, anonymised (no account, serial number or location visible).
