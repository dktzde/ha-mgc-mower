# Example dashboard

A ready-made dashboard for the mower: control, rain settings, condition, and a **weekly mowing schedule** you edit with a few taps. **Not part of the integration**: HACS only installs `custom_components/mgc_mower`, so copy these files by hand.

| File | What it is |
|------|------------|
| `dashboard.yaml` | The dashboard (one view, two sections). |
| `mgc_mower_schedule.yaml` | Package for the schedule section: helpers, preview/compare sensors, send script and automation. |
| `mgc_mower_schedule.jinja` | Template macros used by the package (builds the schedule, the direction rule lives here). |
| `dashboard.de.yaml`, `mgc_mower_schedule.de.yaml` | German version (texts and entity IDs of a German Home Assistant). |
| `dashboard.fr.yaml`, `mgc_mower_schedule.fr.yaml` | French version (texts and entity IDs of a French Home Assistant). |

**Languages:** use the files for the language Home Assistant had when you added the integration (it decides the entity IDs). Use only one language version of the package (all versions create the same helpers). The `.jinja` file is the same for all languages.

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

## Deutsch

Fertiges Beispiel-Dashboard für den Mäher: Steuerung, Regen, Zustand und **Wochen-Mähplan**. HACS installiert es nicht mit, die Dateien also von Hand kopieren.

- Deutsche Fassung: `dashboard.de.yaml` und `mgc_mower_schedule.de.yaml`, dazu `mgc_mower_schedule.jinja` (für alle Sprachen gleich).
- Die Entitäts-IDs passen zu einer Integration, die mit Home Assistant auf Deutsch eingerichtet wurde (z. B. `sensor.<präfix>_akkustand`, `button.<präfix>_mahen_starten`). Ältere Installationen können für einzelne Entitäten noch englische IDs haben – auf der Geräteseite nachsehen und anpassen.
- Einrichtung wie oben unter *Setup*: `my_mower` durch den Präfix ersetzen, `.jinja` nach `<config>/custom_templates/`, Paket nach `<config>/packages/`, Konfiguration prüfen, Home Assistant neu starten, Dashboard im Raw-Konfigurationseditor einfügen.
- Nur **eine** Sprachfassung des Pakets verwenden.

## Français

Tableau de bord d'exemple pour la tondeuse : commande, pluie, état et **planning de tonte hebdomadaire**. HACS ne l'installe pas ; copiez les fichiers à la main.

- Version française : `dashboard.fr.yaml` et `mgc_mower_schedule.fr.yaml`, plus `mgc_mower_schedule.jinja` (identique pour toutes les langues).
- Les ID d'entité correspondent à une intégration ajoutée avec Home Assistant en français (p. ex. `sensor.<préfixe>_niveau_de_batterie`, `button.<préfixe>_demarrer_la_tonte`). Des installations plus anciennes peuvent avoir des ID en anglais pour certaines entités : vérifiez sur la page de l'appareil et adaptez.
- Installation comme ci-dessus (*Setup*) : remplacez `my_mower` par le préfixe, `.jinja` dans `<config>/custom_templates/`, paquet dans `<config>/packages/`, vérifiez la configuration, redémarrez Home Assistant, collez le tableau de bord dans l'éditeur de configuration brute.
- N'utilisez qu'**une seule** version linguistique du paquet.
