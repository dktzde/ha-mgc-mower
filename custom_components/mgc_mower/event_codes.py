"""Known MGC `event_code` values and the help texts for unknown ones.

The mower writes `event_code` into its shadow; the app shows each change as a message in its Message Center.
The meanings below were collected from the app (see `extras/event_codes/`). This module has no Home Assistant
imports, so it can be tested on its own.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlencode

REPO_URL = "https://github.com/dktzde/ha-mgc-mower"
ISSUE_TEMPLATE = "unknown_event_code.yml"
GUIDE_URL = f"{REPO_URL}/tree/main/extras/event_codes"

# event_code -> app text (English, as shown in the Message Center).
KNOWN_EVENT_CODES: dict[int, str] = {
    4: "Device is shutdown",
    18: "Device is fully charged",
    23: "Device is charging",
    41: "It's raining, can't mowing.",
    63: "Mowing is finished",
    66: "Plan's mowing is on",
    235: "Battery temperature too high while charging, charging paused",
    236: "The temperature has returned to normal, continue charging.",
    244: "The PIN code is not unlocked, so this scheduled task cannot be executed.",
    253: "Stop key had been trigger, so this scheduled task cannot be executed.",
}

# Values that mean "no event" and are never reported.
IGNORED_EVENT_CODES: frozenset[int] = frozenset({0})

# Keep the issue link short enough for every browser.
_MAX_FIELD_LENGTH = 200


def normalize_event_code(value: Any) -> int | None:
    """Return the event code as int, or None if there is no usable value."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.lstrip("-").isdigit():
            return int(text)
    return None


def event_code_description(value: Any) -> str | None:
    """Return the app text for a known event code, else None."""
    code = normalize_event_code(value)
    if code is None:
        return None
    return KNOWN_EVENT_CODES.get(code)


def is_known_event_code(value: Any) -> bool:
    """Return True if the code is known (or means "no event")."""
    code = normalize_event_code(value)
    if code is None:
        return False
    return code in KNOWN_EVENT_CODES or code in IGNORED_EVENT_CODES


def is_reportable_event_code(value: Any) -> bool:
    """Return True if the value is a real event code that is not known yet."""
    code = normalize_event_code(value)
    return code is not None and code not in IGNORED_EVENT_CODES and code not in KNOWN_EVENT_CODES


def format_firmware(fw_version: Any) -> str:
    """Return the firmware versions as one short line, e.g. 'ui_board 0.3.5, motor_board 00d3'."""
    if not isinstance(fw_version, Mapping):
        return ""
    parts = [
        f"{key} {value}"
        for key, value in fw_version.items()
        if isinstance(key, str) and isinstance(value, (str, int, float)) and str(value)
    ]
    return ", ".join(parts)


def _clip(value: Any) -> str:
    text = "" if value is None else str(value)
    return text[:_MAX_FIELD_LENGTH]


def build_issue_url(
    *,
    code: int,
    previous_code: int | None,
    seen_at: str,
    mode: Any,
    model: Any,
    firmware: str,
    integration_version: str,
    ha_version: str,
) -> str:
    """Return a link to a new GitHub issue with the form already filled in.

    Only data that identifies no person or device goes into the link: no serial number, IP address or account.
    """
    params = {
        "template": ISSUE_TEMPLATE,
        "title": f"Unknown event_code {code}",
        "event_code": str(code),
        "previous_code": "" if previous_code is None else str(previous_code),
        "seen_at": _clip(seen_at),
        "mode": _clip(mode),
        "model": _clip(model),
        "firmware": _clip(firmware),
        "versions": f"{_clip(integration_version)} / {_clip(ha_version)}",
    }
    query = urlencode({key: value for key, value in params.items() if value})
    return f"{REPO_URL}/issues/new?{query}"


# Notification texts per language. Placeholders: name, code, time, issue_url, guide_url.
_NOTIFICATION_TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "title": "MGC Mower: unknown event code {code}",
        "message": (
            "Your mower **{name}** reported the event code **{code}** on {time}. "
            "The integration does not know this code yet. Please help to improve it, it only takes two minutes:\n\n"
            "1. Open the mower app (e.g. R HOME), tap the speech bubble at the top right and open the **Message Center**.\n"
            "2. Find the message from about {time} (it can be up to 4 minutes earlier). "
            "A screenshot is recommended; copying the message text is fine, too.\n"
            "3. **[Report the code on GitHub]({issue_url})**. The form is already filled in, "
            "just add the screenshot or the text.\n\n"
            "Step-by-step guide with pictures: [how to find the message]({guide_url}).\n\n"
            "Each code is reported only once. You can turn these notifications off in the integration options "
            "(Settings → Devices & services → MGC Mower → Configure)."
        ),
    },
    "de": {
        "title": "MGC Mower: unbekannter Ereigniscode {code}",
        "message": (
            "Dein Mäher **{name}** hat am {time} den Ereigniscode **{code}** gemeldet. "
            "Diesen Code kennt die Integration noch nicht. Bitte hilf bei der Entwicklung, es dauert nur zwei Minuten:\n\n"
            "1. Öffne die App des Mähers (z. B. R HOME), tippe oben rechts auf die Sprechblase und öffne das **Message Center**.\n"
            "2. Suche die Meldung von etwa {time} (sie kann bis zu 4 Minuten früher sein). "
            "Ein Screenshot ist am besten; den Text der Meldung abzuschreiben genügt auch.\n"
            "3. **[Code auf GitHub melden]({issue_url})**. Das Formular ist schon ausgefüllt, "
            "füge nur den Screenshot oder den Text hinzu (Deutsch ist okay).\n\n"
            "Anleitung mit Bildern: [so findest du die Meldung]({guide_url}).\n\n"
            "Jeder Code wird nur einmal gemeldet. Abschalten kannst du diese Benachrichtigungen in den Optionen der "
            "Integration (Einstellungen → Geräte & Dienste → MGC Mower → Konfigurieren)."
        ),
    },
    "fr": {
        "title": "MGC Mower : code d'événement inconnu {code}",
        "message": (
            "Votre tondeuse **{name}** a signalé le code d'événement **{code}** le {time}. "
            "L'intégration ne connaît pas encore ce code. Aidez-nous à l'améliorer, cela ne prend que deux minutes :\n\n"
            "1. Ouvrez l'application de la tondeuse (p. ex. R HOME), touchez la bulle en haut à droite et ouvrez le "
            "**Message Center**.\n"
            "2. Cherchez le message d'environ {time} (il peut dater de jusqu'à 4 minutes plus tôt). "
            "Une capture d'écran est recommandée ; recopier le texte du message suffit aussi.\n"
            "3. **[Signaler le code sur GitHub]({issue_url})**. Le formulaire est déjà rempli, "
            "ajoutez seulement la capture d'écran ou le texte (le français est accepté).\n\n"
            "Guide avec images : [comment trouver le message]({guide_url}).\n\n"
            "Chaque code n'est signalé qu'une seule fois. Vous pouvez désactiver ces notifications dans les options "
            "de l'intégration (Paramètres → Appareils et services → MGC Mower → Configurer)."
        ),
    },
}


def notification_texts(
    language: str | None, *, name: str, code: int, time: str, issue_url: str
) -> tuple[str, str]:
    """Return (title, message) for the notification in the given language (fallback English)."""
    lang = (language or "en").split("-")[0].split("_")[0].lower()
    texts = _NOTIFICATION_TEXTS.get(lang, _NOTIFICATION_TEXTS["en"])
    values = {
        "name": name,
        "code": code,
        "time": time,
        "issue_url": issue_url,
        "guide_url": GUIDE_URL,
    }
    return texts["title"].format(**values), texts["message"].format(**values)
