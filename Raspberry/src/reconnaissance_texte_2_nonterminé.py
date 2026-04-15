import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


# =========================
# ENUM + DATA CLASS
# =========================
class Intent(Enum):
    UNKNOWN = "UNKNOWN"
    AVANCER = "AVANCER"
    RECULER = "RECULER"
    TOURNER_GAUCHE = "TOURNER_GAUCHE"
    TOURNER_DROITE = "TOURNER_DROITE"
    DETECTER_COULEUR = "DETECTER_COULEUR"
    STOP = "STOP"


@dataclass
class Command:
    intent: Intent
    value: Optional[float] = None
    unit: Optional[str] = None
    color: Optional[str] = None
    raw_text: str = ""
    normalized_text: str = ""
    valid: bool = False
    error: Optional[str] = None


# =========================
# PATTERNS
# =========================
ACTION_PATTERNS = [
    (Intent.STOP, ["stop", "arret", "arrete", "immobile"]),
    (Intent.DETECTER_COULEUR, [
        "detecte la couleur", "detecter la couleur",
        "cherche la couleur", "identifie la couleur",
        "reconnais la couleur", "analyse la couleur",
        "quelle couleur", "va vers la couleur",
        "detecte l objet"
    ]),
    (Intent.TOURNER_GAUCHE, [
        "tourne a gauche", "tourner a gauche",
        "va a gauche", "pivote a gauche", "braque a gauche"
    ]),
    (Intent.TOURNER_DROITE, [
        "tourne a droite", "tourner a droite", "tourne",
        "va a droite", "pivote a droite", "braque a droite"
    ]),
    (Intent.RECULER, ["recule", "reculer", "marche arriere"]),
    (Intent.AVANCER, [
        "avance", "avancer", "va tout droit",
        "continue", "poursuis"
    ]),
]


COLOR_ALIASES = {
    "rouge": "rouge", "vert": "vert", "verte": "vert",
    "bleu": "bleu", "bleue": "bleu", "jaune": "jaune",
    "noir": "noir", "noire": "noir", "blanc": "blanc",
    "blanche": "blanc", "orange": "orange",
    "gris": "gris", "grise": "gris",
    "rose": "rose", "violet": "violet",
    "violette": "violet", "marron": "marron",
}


UNIT_ALIASES = {
    "m": "m", "metre": "m", "metres": "m",
    "cm": "cm", "centimetre": "cm", "centimetres": "cm",
    "degre": "deg", "degres": "deg",
    "s": "s", "sec": "s", "seconde": "s", "secondes": "s",
}


# =========================
# NORMALISATION
# =========================
def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def normalize_text(text: str) -> str:
    text = strip_accents(text.lower())
    text = text.replace("'", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# INTENT DETECTION
# =========================
def detect_intent(text: str) -> Intent:
    for intent, patterns in ACTION_PATTERNS:
        for pattern in patterns:
            if re.search(rf"\b{re.escape(pattern)}\b", text):
                return intent
    return Intent.UNKNOWN


# =========================
# EXTRACTION VALEUR + UNITE
# =========================
def extract_value_and_unit(text: str):
    match = re.search(
        r"(\d+(?:[\.,]\d+)?)\s*(m|metre|metres|cm|centimetre|centimetres|degre|degres|s|sec|seconde|secondes)?\b",
        text
    )

    if not match:
        return None, None

    value = float(match.group(1).replace(",", "."))
    unit = UNIT_ALIASES.get(match.group(2), None) if match.group(2) else None

    return value, unit


# =========================
# EXTRACTION COULEUR
# =========================
def extract_color(text: str) -> Optional[str]:
    for color in COLOR_ALIASES:
        if re.search(rf"\b{re.escape(color)}\b", text):
            return COLOR_ALIASES[color]
    return None


# =========================
# CONVERSION
# =========================
def convert_value(value: float, unit: Optional[str]):
    if value is None:
        return None, None

    if unit == "cm":
        return value / 100.0, "m"

    return value, unit


# =========================
# VALIDATION
# =========================
def validate_command(cmd: Command) -> Command:

    if cmd.intent == Intent.UNKNOWN:
        cmd.error = "Commande inconnue"
        return cmd

    if cmd.intent == Intent.STOP:
        cmd.valid = True
        return cmd

    if cmd.intent in {Intent.AVANCER, Intent.RECULER}:
        if cmd.value is None:
            cmd.value = 1.0
        if cmd.unit is None:
            cmd.unit = "m"

        cmd.value, cmd.unit = convert_value(cmd.value, cmd.unit)

        if not (0 < cmd.value <= 5):
            cmd.error = "Distance doit être entre 0 et 5 mètres"
            return cmd

    if cmd.intent in {Intent.TOURNER_GAUCHE, Intent.TOURNER_DROITE}:
        if cmd.value is None:
            cmd.value = 90.0
        if cmd.unit is None:
            cmd.unit = "deg"

        if not (0 < cmd.value <= 360):
            cmd.error = "Angle doit être entre 0 et 360 degrés"
            return cmd

    if cmd.intent == Intent.DETECTER_COULEUR and cmd.color is None:
        cmd.color = "ANY"

    cmd.valid = True
    return cmd


# =========================
# PARSER UNIQUE (inchangé)
# =========================
def parse_command(text: str) -> Command:
    normalized = normalize_text(text)

    intent = detect_intent(normalized)
    value, unit = extract_value_and_unit(normalized)
    color = extract_color(normalized)

    cmd = Command(
        intent=intent,
        value=value,
        unit=unit,
        color=color,
        raw_text=text,
        normalized_text=normalized,
    )

    return validate_command(cmd)


# =========================
# 🔥 NOUVEAU : MULTI COMMANDES → LISTE DE DICTS
# =========================
def parse_to_robot_actions(text: str) -> List[dict]:

    parts = re.split(r"\b(puis|et|ensuite)\b|,", normalize_text(text))

    actions = []

    for part in parts:
        part = part.strip()

        if not part or part in {"puis", "et", "ensuite"}:
            continue

        cmd = parse_command(part)

        if not cmd.valid:
            actions.append({"ok": False, "error": cmd.error, "raw": part})
            continue

        actions.append({
            "ok": True,
            "intent": cmd.intent.value,
            "value": cmd.value,
            "unit": cmd.unit,
            "target_color": cmd.color
        })

    return actions


# =========================
# TEST
# =========================

def interactive_demo():
    print("Tape une commande ('quit' pour quitter)")

    while True:
        text = input(">> ")

        if text.lower() in {"quit", "exit"}:
            break

        cmd = parse_command(text)
        payload = parse_to_robot_actions(text)

        print("Parsed:", cmd)
        print("Payload:", payload)

if __name__ == "__main__":
    interactive_demo()

