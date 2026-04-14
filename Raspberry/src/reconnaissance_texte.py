import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


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


ACTION_PATTERNS = [
    (Intent.STOP, [
        "stop", "arret", "arrete", "arrete toi", "arretez vous", "immobile"
    ]),
    (Intent.DETECTER_COULEUR, [
        "detecte la couleur", "detecter la couleur", "detecte une couleur",
        "cherche la couleur", "identifie la couleur", "reconnais la couleur",
        "reconnaissance de couleur", "analyse la couleur", "lis la couleur",
        "quelle est la couleur", "quelle couleur", "va vers la couleur", "allez vers la couleur", "detecte", "detecte l'objetdetecte l'objet "
    ]),
    (Intent.TOURNER_GAUCHE, [
        "tourne a gauche", "tourner a gauche", "tournez a gauche",
        "va a gauche", "allez a gauche", "pivote a gauche", "braque a gauche"
    ]),
    (Intent.TOURNER_DROITE, [
        "tourne a droite", "tourner a droite", "tournez a droite",
        "va a droite", "allez a droite", "pivote a droite", "braque a droite"
    ]),
    (Intent.RECULER, [
        "recule", "reculer", "reculez", "va en arriere", "allez en arriere",
        "marche arriere", "fais marche arriere"
    ]),
    (Intent.AVANCER, [
        "avance", "avancer", "avancez", "va devant", "va en avant",
        "va tout droit", "allez devant", "allez en avant", "allez tout droit",
        "tout droit", "continue", "continuer", "continuez", "poursuis",
        "poursuivre", "poursuivez", "va"
    ]),
]

COLOR_ALIASES = {
    "rouge": "rouge",
    "vert": "vert",
    "verte": "vert",
    "bleu": "bleu",
    "bleue": "bleu",
    "jaune": "jaune",
    "noir": "noir",
    "noire": "noir",
    "blanc": "blanc",
    "blanche": "blanc",
    "orange": "orange",
    "gris": "gris",
    "grise": "gris",
    "rose": "rose",
    "violet": "violet",
    "violette": "violet",
    "marron": "marron",
}

UNIT_ALIASES = {
    "m": "m",
    "metre": "m",
    "metres": "m",
    "cm": "cm",
    "centimetre": "cm",
    "centimetres": "cm",
    "degre": "deg",
    "degres": "deg",
    "s": "s",
    "sec": "s",
    "seconde": "s",
    "secondes": "s",
}

FILLER_WORDS = {
    "de", "du", "des", "le", "la", "les", "un", "une", "vers", "sur", "au", "aux"
}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize_text(text: str) -> str:
    text = strip_accents(text.lower())
    text = text.replace("'", " ")
    text = re.sub(r"[^a-z0-9.,\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def canonicalize_units(text: str) -> str:
    replacements = {
        "metres": "metres",
        "metre": "metre",
        "centimetres": "centimetres",
        "centimetre": "centimetre",
        "degres": "degres",
        "degre": "degre",
        "secondes": "secondes",
        "seconde": "seconde",
    }
    for src, dst in replacements.items():
        text = re.sub(rf"\b{src}\b", dst, text)
    return text


def detect_intent(text: str) -> Intent:
    for intent, patterns in ACTION_PATTERNS:
        for pattern in patterns:
            if pattern in text:
                return intent
    tokens = text.split()
    if "gauche" in tokens and any(t.startswith("tourn") or t in {"pivote", "braque"} for t in tokens):
        return Intent.TOURNER_GAUCHE
    if "droite" in tokens and any(t.startswith("tourn") or t in {"pivote", "braque"} for t in tokens):
        return Intent.TOURNER_DROITE
    return Intent.UNKNOWN


def extract_value_and_unit(text: str):
    match = re.search(
        r"(-?\d+(?:[\.,]\d+)?)\s*(m|metre|metres|cm|centimetre|centimetres|degre|degres|s|sec|seconde|secondes)?\b", text)
    if not match:
        return None, None
    value = float(match.group(1).replace(",", "."))
    raw_unit = match.group(2)
    unit = UNIT_ALIASES.get(raw_unit, None) if raw_unit else None
    return value, unit


def extract_color(text: str) -> Optional[str]:
    for word in text.split():
        if word in COLOR_ALIASES:
            return COLOR_ALIASES[word]
    return None


def convert_value(value: float, unit: Optional[str]):
    if value is None:
        return None, None
    if unit == "cm":
        return value / 100.0, "m"
    if unit == "infini":
        return float("inf"), "m"
    return value, unit


def validate_command(cmd: Command) -> Command:
    if cmd.intent == Intent.UNKNOWN:
        cmd.error = "Commande inconnue"
        return cmd

    if cmd.intent in {Intent.AVANCER, Intent.RECULER}:
        if cmd.value is None:
            cmd.error = "Distance manquante"
            return cmd
        if cmd.unit is None:
            cmd.unit = "m"
        cmd.value, cmd.unit = convert_value(cmd.value, cmd.unit)
        if cmd.unit != "m":
            cmd.error = "Unite invalide pour un deplacement"
            return cmd
        if not (0 < cmd.value <= 10):
            cmd.error = "Distance hors limites"
            return cmd

    elif cmd.intent in {Intent.TOURNER_GAUCHE, Intent.TOURNER_DROITE}:
        if cmd.value is None:
            cmd.value = 90.0
            cmd.unit = "deg"
        if cmd.unit is None:
            cmd.unit = "deg"
        if cmd.unit != "deg":
            cmd.error = "Unite invalide pour une rotation"
            return cmd
        if not (0 < cmd.value <= 360):
            cmd.error = "Angle hors limites"
            return cmd

    elif cmd.intent == Intent.DETECTER_COULEUR:
        if cmd.color is None:
            cmd.color = "ANY"

    elif cmd.intent == Intent.STOP:
        pass

    cmd.valid = True
    return cmd


def parse_command(text: str) -> Command:
    normalized = canonicalize_units(normalize_text(text))
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


def command_to_robot_payload(cmd: Command) -> dict:
    if not cmd.valid:
        return {"ok": False, "error": cmd.error}
    payload = {"ok": True, "intent": cmd.intent.value}
    if cmd.value is not None:
        payload["value"] = cmd.value
    if cmd.unit is not None:
        payload["unit"] = cmd.unit
    if cmd.color is not None:
        payload["color"] = cmd.color
    return payload


def demo(commands: List[str]):
    for text in commands:
        cmd = parse_command(text)
        print(f"Input: {text}")
        print(f"Parsed: {cmd}")
        print(f"Payload: {command_to_robot_payload(cmd)}")
        print("-" * 60)


def interactive_demo():
    print("Tape une commande (ou 'quit' pour quitter)")

    while True:
        text = input(">> ")

        if text.lower() in {"quit", "exit"}:
            break

        cmd = parse_command(text)
        payload = command_to_robot_payload(cmd)

        print("Parsed:", cmd)
        print("Payload:", payload)
        print("-" * 40)


if __name__ == "__main__":
    interactive_demo()
    demo(samples)
