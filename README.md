<p align="center">
  <img src="images/redkey.png" alt="Redkey" height="60">
  &nbsp;&nbsp;
  <img src="custom_components/mgc_mower/brand/icon.png" alt="Handwise" height="60">
</p>

# MGC Mower

Home Assistant integration for **MGC robotic lawn mowers** on the Anthbot cloud: **Redkey MGC1000 / MGC500, Handwise MGC500 (MGC01 500), Redroad MGC500, Anthbot Pion** and possibly EZVIZ RM600.

[English](#english) · [Français](#français) · [Deutsch](#deutsch)

---

# English

## Installation

**HACS (custom repository):** HACS → ⋮ → *Custom repositories* → add `https://github.com/dktzde/ha-mgc-mower`, category *Integration* → download → restart Home Assistant.

**Manual:** copy `custom_components/mgc_mower` to `config/custom_components/mgc_mower` and restart.

Then: *Settings → Devices & services → Add integration → MGC Mower* and sign in with your app account (Redkey: R HOME account, API host `api.anthbot.com`).

> Coming from Handwise-HA? Remove it first, otherwise the mower shows up twice.

## Why this fork?

[Handwise-HA](https://github.com/MTTPoll/handwise-ha) did not write the rain wait time correctly on MGC mowers. This fork fixes that and adds the weekly mowing schedule.

**Works**
- Rain wait time is written correctly (0–12 h in 0.1 h steps; the app only offers 1–3 h)
- Rain detection on/off
- Writing the weekly mowing schedule (`mgc_mower.set_mowing_schedule`)
- Everything from Handwise-HA: start, pause, dock, battery, status, progress, cutting height, zones, diagnostics …

**Example dashboard:** control, rain settings and a weekly mowing schedule with a few taps, see [extras/dashboard](extras/dashboard/).

**To do**
- The message centre can't be read yet

```yaml
action: mgc_mower.set_mowing_schedule
target:
  entity_id: lawn_mower.your_mower
data:
  entries:
    - weekdays: [mon, wed, fri]
      start: "17:00"
      end: "19:00"        # optional, empty = until finished
      cutter_height: 55   # 30–70 mm
      direction: cross    # perpendicular | parallel | cross
```

The app always sends the complete schedule, so a change in the app overwrites the one from Home Assistant and vice versa.

## Models

| Model | Status |
|---|---|
| Redkey MGC1000 | ✅ tested (this fork) |
| Handwise MGC500 (MGC01 500) | ✅ tested (upstream) |
| Redkey MGC500, Redroad MGC500, Anthbot Pion | ❔ largely identical hardware, should work |
| EZVIZ RM600 | ⚠️ largely identical hardware, but may use a different cloud |

Feedback on other models is welcome: please open an issue.

> 🌱 **Hobby project:** I maintain this in my spare time and answer at my own pace. Pull requests are welcome.

> ⚠️ **Caution:** my mower is already in winter hibernation. The changes have only been tested briefly.

## Thanks

Many thanks to [MTTPoll/handwise-ha](https://github.com/MTTPoll/handwise-ha). This integration is built on it. Unofficial project, not affiliated with Redkey, Handwise, Anthbot, Redroad or EZVIZ.

History: [CHANGELOG](CHANGELOG.md). Up to 0.1.0 by MTTPoll, from 0.2.0 by dktzde.

---

# Français

## Installation

**HACS (dépôt personnalisé) :** HACS → ⋮ → *Dépôts personnalisés* → ajouter `https://github.com/dktzde/ha-mgc-mower`, catégorie *Intégration* → télécharger → redémarrer Home Assistant.

**Manuelle :** copier `custom_components/mgc_mower` dans `config/custom_components/mgc_mower` et redémarrer.

Ensuite : *Paramètres → Appareils et services → Ajouter une intégration → MGC Mower* et se connecter avec le compte de l'application (Redkey : compte R HOME, hôte API `api.anthbot.com`).

> Vous utilisiez Handwise-HA ? Supprimez-la d'abord, sinon la tondeuse apparaît deux fois.

## Pourquoi ce fork ?

[Handwise-HA](https://github.com/MTTPoll/handwise-ha) n'écrivait pas correctement le délai d'attente après la pluie sur les tondeuses MGC. Ce fork corrige ce problème et ajoute le planning de tonte hebdomadaire.

**Fonctionne**
- Délai d'attente après la pluie écrit correctement (0–12 h par pas de 0,1 h ; l'application ne propose que 1–3 h)
- Détection de pluie activée/désactivée
- Écriture du planning de tonte hebdomadaire (`mgc_mower.set_mowing_schedule`, exemple voir [English](#english))
- Tout ce que fait Handwise-HA : démarrage, pause, retour à la base, batterie, état, progression, hauteur de coupe, zones, diagnostic …

**Tableau de bord d'exemple :** commande, réglages pluie et planning hebdomadaire en quelques clics, voir [extras/dashboard](extras/dashboard/) (en anglais).

**À faire**
- Le centre de messages ne peut pas encore être lu

L'application envoie toujours le planning complet : une modification dans l'application remplace celle de Home Assistant et inversement.

## Modèles

| Modèle | Statut |
|---|---|
| Redkey MGC1000 | ✅ testé (ce fork) |
| Handwise MGC500 (MGC01 500) | ✅ testé (upstream) |
| Redkey MGC500, Redroad MGC500, Anthbot Pion | ❔ matériel très similaire, devrait fonctionner |
| EZVIZ RM600 | ⚠️ matériel très similaire, mais utilise peut-être un autre cloud |

Vos retours sur d'autres modèles sont les bienvenus : ouvrez une issue.

> 🌱 **Projet de loisir :** je le maintiens sur mon temps libre et réponds à mon rythme. Les pull requests sont les bienvenues.

> ⚠️ **Attention :** ma tondeuse est déjà en hivernage. Les modifications n'ont été testées que brièvement.

## Remerciements

Un grand merci à [MTTPoll/handwise-ha](https://github.com/MTTPoll/handwise-ha), sur lequel repose cette intégration. Projet non officiel, sans lien avec Redkey, Handwise, Anthbot, Redroad ou EZVIZ.

Historique : [CHANGELOG](CHANGELOG.md). Jusqu'à la 0.1.0 par MTTPoll, à partir de la 0.2.0 par dktzde.

---

# Deutsch

## Installation

**HACS (benutzerdefiniertes Repository):** HACS → ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/dktzde/ha-mgc-mower` hinzufügen, Kategorie *Integration* → herunterladen → Home Assistant neu starten.

**Manuell:** `custom_components/mgc_mower` nach `config/custom_components/mgc_mower` kopieren und neu starten.

Danach: *Einstellungen → Geräte & Dienste → Integration hinzufügen → MGC Mower* und mit dem App-Konto anmelden (Redkey: R-HOME-Konto, API-Host `api.anthbot.com`).

> Du nutzt bisher Handwise-HA? Entferne es vorher, sonst erscheint der Mäher doppelt.

## Warum dieser Fork?

[Handwise-HA](https://github.com/MTTPoll/handwise-ha) hat bei MGC-Mähern die Regen-Wartezeit nicht richtig geschrieben. Dieser Fork behebt das und ergänzt den Wochen-Mähplan.

**Funktioniert**
- Regen-Wartezeit wird korrekt geschrieben (0–12 h in 0,1-h-Schritten; die App bietet nur 1–3 h)
- Regenerkennung ein/aus
- Wochen-Mähplan schreiben (`mgc_mower.set_mowing_schedule`, Beispiel siehe [English](#english))
- Alles aus Handwise-HA: Start, Pause, Zurück zur Station, Akku, Status, Fortschritt, Schnitthöhe, Zonen, Diagnose …

**Beispiel-Dashboard:** Steuerung, Regen-Einstellungen und Wochen-Mähplan mit ein paar Klicks, siehe [extras/dashboard](extras/dashboard/) (englisch).

**Noch offen**
- Das Message Center kann noch nicht ausgelesen werden

Die App schickt immer den kompletten Plan. Eine Änderung in der App überschreibt deshalb den Plan aus Home Assistant und umgekehrt.

## Modelle

| Modell | Status |
|---|---|
| Redkey MGC1000 | ✅ getestet (dieser Fork) |
| Handwise MGC500 (MGC01 500) | ✅ getestet (Upstream) |
| Redkey MGC500, Redroad MGC500, Anthbot Pion | ❔ weitgehend baugleich, sollte funktionieren |
| EZVIZ RM600 | ⚠️ weitgehend baugleich, nutzt aber eventuell eine andere Cloud |

Rückmeldungen zu weiteren Modellen sind willkommen, bitte als Issue.

> 🌱 **Hobbyprojekt:** Ich pflege das in meiner Freizeit und antworte in meinem eigenen Tempo. Pull Requests sind willkommen.

> ⚠️ **Achtung:** Mein Mäher ist schon im Winterschlaf. Die Änderungen wurden nur kurz getestet.

## Danke

Vielen Dank an [MTTPoll/handwise-ha](https://github.com/MTTPoll/handwise-ha), auf dem diese Integration aufbaut. Inoffizielles Projekt, keine Verbindung zu Redkey, Handwise, Anthbot, Redroad oder EZVIZ.

Historie: [CHANGELOG](CHANGELOG.md). Bis 0.1.0 von MTTPoll, ab 0.2.0 von dktzde.

---

*Entstanden mit Hilfe von [Claude Code in Home Assistant](https://github.com/dktzde/hass-claude-code). Im Gegensatz zum Mäher hält es keinen Winterschlaf.*
