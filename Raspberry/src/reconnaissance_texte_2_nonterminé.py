import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# =========================
# INTENTIONS
# =========================
class Intent(Enum):
    UNKNOWN = "UNKNOWN"
    AVANCER = "AVANCER"
    RECULER = "RECULER"
    TOURNER_GAUCHE = "TOURNER_GAUCHE"
    TOURNER_DROITE = "TOURNER_DROITE"
    DETECTER = "DETECTER"   # 👈 NOUVELLE INTENTION (capteur)
    STOP = "STOP"


# =========================
# STRUCTURE COMMANDE
# =========================
@dataclass
class Command:
    intent: Intent
    value: Optional[float] = None
    unit: Optional[str] = None
    target_color: Optional[str] = None  # 👈 objectif couleur séparé

    raw_text: str = ""
    normalized_text: str = ""

    valid: bool = False
    error: Optional[str] = None


# =========================
# COULEURS
# =========================
COLOR_ALIASES = {
    "rouge": "rouge",
    "vert": "vert",
    "bleu": "bleu",
    "jaune": "jaune",
    "noir": "noir",
    "blanc": "blanc",
}


# =========================
# UNITES
# =========================
UNIT_ALIASES = {
    "m": "m",
    "metre": "m",
    "metres": "m",
    "cm": "cm",
    "centimetre": "cm",
    "centimetres": "cm",
    "deg": "deg",
    "degre": "deg",
    "degres": "deg",
}


# =========================
# NORMALISATION
# =========================
def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("'", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# DETECTER INTENTION
# =========================
def detect_intent(text: str) -> Intent:

    if "stop" in text:
        return Intent.STOP

    if "avance" in text:
        return Intent.AVANCER

    if "recule" in text:
        return Intent.RECULER

    if "gauche" in text:
        return Intent.TOURNER_GAUCHE

    if "droite" in text:
        return Intent.TOURNER_DROITE

    # 👇 NOUVELLE INTENTION
    if "detecte" in text or "cherche" in text:
        return Intent.DETECTER

    return Intent.UNKNOWN


# =========================
# EXTRACTION VALEUR
# =========================
def extract_value_and_unit(text: str):
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(\w+)?", text)

    if not match:
        return None, None

    value = float(match.group(1).replace(",", "."))
    unit = UNIT_ALIASES.get(match.group(2), None) if match.group(2) else None

    return value, unit


# =========================
# EXTRACTION COULEUR (OPTION OBJECTIF)
# =========================
def extract_target_color(text: str) -> Optional[str]:
    for color in COLOR_ALIASES:
        if re.search(rf"\b{color}\b", text):
            return COLOR_ALIASES[color]
    return None


# =========================
# VALIDATION
# =========================
def validate(cmd: Command) -> Command:

    if cmd.intent == Intent.UNKNOWN:
        cmd.error = "Commande inconnue"
        return cmd

    # STOP
    if cmd.intent == Intent.STOP:
        cmd.valid = True
        return cmd

    # AVANCER / RECULER
    if cmd.intent in {Intent.AVANCER, Intent.RECULER}:

        if cmd.value is None:
            cmd.value = 1.0

        if cmd.unit == "cm":
            cmd.value /= 100
            cmd.unit = "m"

        if cmd.unit is None:
            cmd.unit = "m"

        if not (0 < cmd.value <= 5):
            cmd.error = "Distance doit être entre 0 et 5 mètres"
            return cmd

    # ROTATION
    if cmd.intent in {Intent.TOURNER_GAUCHE, Intent.TOURNER_DROITE}:

        if cmd.value is None:
            cmd.value = 90

        if cmd.unit is None:
            cmd.unit = "deg"

        if not (0 < cmd.value <= 360):
            cmd.error = "Angle doit être entre 0 et 360 degrés"
            return cmd

    # DETECTER
    if cmd.intent == Intent.DETECTER:
        # ici pas obligatoire d'avoir une couleur
        pass

    cmd.valid = True
    return cmd


# =========================
# PIPELINE PRINCIPAL
# =========================
def parse_command(text: str) -> Command:

    normalized = normalize_text(text)

    intent = detect_intent(normalized)
    value, unit = extract_value_and_unit(normalized)
    color = extract_target_color(normalized)

    cmd = Command(
        intent=intent,
        value=value,
        unit=unit,
        target_color=color,
        raw_text=text,
        normalized_text=normalized
    )

    return validate(cmd)


# =========================
# FORMAT ROBOT (IMPORTANT)
# =========================
def command_to_robot_payload(cmd: Command) -> dict:

    if not cmd.valid:
        return {"ok": False, "error": cmd.error}

    payload = {
        "ok": True,
        "intent": cmd.intent.value
    }

    if cmd.value is not None:
        payload["value"] = cmd.value

    if cmd.unit is not None:
        payload["unit"] = cmd.unit

    if cmd.target_color is not None:
        payload["target_color"] = cmd.target_color  # 👈 IMPORTANT

    return payload


def interactive_demo():
    print("Tape une commande ('quit' pour quitter)")

    while True:
        text = input(">> ")

        if text.lower() in {"quit", "exit"}:
            break

        cmd = parse_command(text)
        payload = command_to_robot_payload(cmd)

        print("Parsed:", cmd)
        print("Payload:", payload)


if __name__ == "__main__":
    interactive_demo()