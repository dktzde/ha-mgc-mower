# Changelog

Dates are release dates (YYYY-MM-DD).

---

## MGC Mower, maintained by [dktzde](https://github.com/dktzde) (from 0.2.0)

### 0.2.1 – 2026-10-28

- **Extras:** `extras/dashboard`, an example dashboard (control, rain settings, condition) with a weekly mowing schedule editor (package + template macros). Not installed by HACS.
- **Docs:** hobby project note in the README, issue templates for bug reports and model feedback.

### 0.2.0 – 2026-10-14

First release of MGC Mower. Forked from Handwise-HA at commit `a292dbc` (2026-06-09).

- **Changed:** renamed Handwise-HA → MGC Mower, domain `handwise_ha` → `mgc_mower`.
  Breaking: remove Handwise-HA, set the integration up again and update automations.
- **Fixed:** rain wait time on MGC firmware. Now sent as `mow_delay` in minutes, range 0–12 h.
- **Fixed:** rain detection on/off on MGC firmware (`ctl_rainer` 1/0).
- **Added:** weekly mowing schedule: service `mgc_mower.set_mowing_schedule` and a schedule sensor.
- **Docs:** new short README in English, French and German, Redkey and Handwise logos.
- **Extras:** `extras/shadow_capture`, a debug patch (service `capture_shadow`) for reading the mower's cloud shadows. Not installed by HACS.

---

## Handwise-HA, by [MTTPoll](https://github.com/MTTPoll) (up to 0.1.0)

Original project: [MTTPoll/handwise-ha](https://github.com/MTTPoll/handwise-ha). Everything in this section is MTTPoll's work.

### 0.1.0 – 2026-06-07

First release for Handwise mowers on the Handwise / Anthbot cloud: lawn mower entity (start, pause, return to dock), battery, status, mowing progress, mowed area, cutting height, Wi-Fi, rain detection, zone mowing and diagnostics.

Commit `a292dbc` (2026-06-09, manifest formatting) came after this release and is the last upstream commit included in MGC Mower.
