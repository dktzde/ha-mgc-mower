# Example dashboard

A ready-made dashboard for the mower: control, rain settings, condition, and a **weekly mowing schedule** you edit with a few taps. **Not part of the integration**: HACS only installs `custom_components/mgc_mower`, so copy these files by hand.

| File | What it is |
|------|------------|
| `dashboard.yaml` | The dashboard (one view, two sections). |
| `mgc_mower_schedule.yaml` | Package for the schedule section: helpers, preview/compare sensors, send script and automation. |
| `mgc_mower_schedule.jinja` | Template macros used by the package (builds the schedule, the direction rule lives here). |

Only want the control part? Use `dashboard.yaml` alone and delete the second section ("Mowing schedule (week)").

## What it looks like

**Lawn mower:** mower state, battery, status, progress · buttons *Start mowing* (asks first), *Pause*, *Return to dock* · rain detection on/off and wait time after rain (0–12 h) · connection, Wi-Fi, error, safety trigger, PIN, cutting height, mowed area · 48 h history of battery and mower state.

**Mowing schedule (week):** tick the days, set one start time, an end time or *Until finished*, and one cutting height for all days. A status line shows the setting, the schedule stored in the mower and whether they match. Every change is sent to the mower automatically after 15 s (only if the mower differs); *Send now* sends it at once.

Direction rule: **Monday = cross, the other ticked days alternate perpendicular / parallel** (starting with perpendicular), so the lawn is cut in a different direction each time. Change it in `mgc_schedule_entries` in the `.jinja` file if you prefer something else.

The schedule is stored in the mower and runs without Home Assistant. The app always sends the complete schedule: a change in the app replaces the one from Home Assistant (status "Differs") until you change something in the dashboard or press *Send now*.

## Setup

1. **Entity prefix:** find your mower under *Settings → Devices & services → MGC Mower*, e.g. `lawn_mower.r_home_mower` → prefix `r_home_mower`. Replace every `my_mower` in `dashboard.yaml` and `mgc_mower_schedule.yaml` with it.
2. **Entity names:** the examples use the English entity IDs (`button.<prefix>_start_mowing`, `sensor.<prefix>_battery_level`, `sensor.<prefix>_mowing_schedule` …). If Home Assistant was set to another language when you added the integration, the IDs are in that language (German: `button.<prefix>_mahen_starten`, `sensor.<prefix>_mahplan` …). Look them up on the device page and adjust. Cards with an unknown entity show a yellow warning.
3. **Schedule (optional):**
   - Copy `mgc_mower_schedule.jinja` to `<config>/custom_templates/`.
   - Copy `mgc_mower_schedule.yaml` to `<config>/packages/`. Packages need this once in `configuration.yaml`:
     ```yaml
     homeassistant:
       packages: !include_dir_named packages
     ```
   - Check the configuration (*Developer tools → YAML → Check configuration*) and restart Home Assistant (new helpers and templates need a restart the first time).
   - Set the helpers once to the plan you want. Nothing is sent on start-up; the first change in the dashboard sends it.
4. **Dashboard:** *Settings → Dashboards → Add dashboard → New dashboard from scratch*, open it, *⋮ → Edit dashboard → ⋮ → Raw configuration editor*, replace everything with `dashboard.yaml`, save.

Requires Home Assistant 2024.8 or newer (sections view, heading card). No custom cards are needed.
