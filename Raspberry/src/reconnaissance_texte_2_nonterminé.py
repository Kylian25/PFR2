import re
import unicodedata
import sys
sys.path.append(r"C:\Users\CMF5190A\Downloads")

import detection
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
    ZIGZAG = "ZIGZAG"


@dataclass
class Command:
    intent: Intent
    value: Optional[float] = None
    unit: Optional[str] = None
    color: Optional[str] = None
    shape: Optional[str] = None 
    raw_text: str = ""
    normalized_text: str = ""
    valid: bool = False
    error: Optional[str] = None


ACTION_PATTERNS = [
    (Intent.STOP, [
        "stop", "halt", "freeze",
        "arret", "arrete", "immobile"
    ]),

    (Intent.DETECTER_COULEUR, [
        "detecte la couleur", "detecter la couleur",
        "cherche la couleur", "identifie la couleur",
        "analyse la couleur", "quelle couleur",
        "detecte l objet",

        "detect color", "find color", "identify color",
        "what color", "scan color", "recognize color"
    ]),

    (Intent.TOURNER_GAUCHE, [
        "tourne a gauche", "tourner a gauche",
        "va a gauche", "pivote a gauche",

        "turn left", "go left", "rotate left"
    ]),

    (Intent.TOURNER_DROITE, [
        "tourne a droite", "tourner a droite",
        "va a droite", "pivote a droite", "tourne",

        "turn right", "go right", "rotate right", "turn"
    ]),

    (Intent.RECULER, [
        "recule", "reculer",

        "back", "backward", "go back", "move back"
    ]),

    (Intent.AVANCER, [
        "avance", "avancer", "va tout droit",
        "continue",

        "forward", "go forward", "move forward",
        "go straight", "move ahead", "continue"
    ]),
    
    (Intent.ZIGZAG, ["zigzag", "faire zigzag"]),
]


COLOR_ALIASES = {
    "rouge": "red", "red": "red",
    "vert": "green", "verte": "green", "green": "green",
    "bleu": "blue", "blue": "blue",
    "jaune": "yellow", "yellow": "yellow",
    "noir": "black", "black": "black",
    "blanc": "white", "white": "white",
    "orange": "orange",
    "rose": "pink", "pink": "pink",
    "violet": "purple", "purple": "purple",
}


SHAPE_ALIASES = {
    "balle": "BALLE",
    "cube": "CUBE",
}


UNIT_ALIASES = {
    "m": "m", "meter": "m", "meters": "m",
    "metre": "m", "metres": "m",

    "cm": "cm", "centimeter": "cm", "centimeters": "cm",
    "centimetre": "cm", "centimetres": "cm",

    "deg": "deg", "degree": "deg", "degrees": "deg",
    "degre": "deg", "degres": "deg",
}


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def normalize_text(text: str) -> str:
    text = strip_accents(text.lower())

    text = text.replace("°", " deg ")
    text = text.replace("'", " ")
    text = text.replace("-", " ")

    text = text.replace("to the", "")
    text = text.replace("go to", "go")

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_intent(text: str) -> Intent:
    for intent, patterns in ACTION_PATTERNS:
        for p in patterns:
            if re.search(rf"\b{re.escape(p)}\b", text):
                return intent
    return Intent.UNKNOWN


def extract_value_and_unit(text: str):
    match = re.search(
        r"(?:de\s*)?(\d+(?:[\.,]\d+)?)\s*(m|meter|meters|metre|metres|cm|centimeter|centimeters|centimetre|centimetres|deg|degree|degrees|degre|degres)?",
        text
    )

    if not match:
        return None, None

    value = float(match.group(1).replace(",", "."))
    unit = UNIT_ALIASES.get(match.group(2), None) if match.group(2) else None

    return value, unit


def extract_color(text: str):
    for c in COLOR_ALIASES:
        if re.search(rf"\b{c}\b", text):
            return COLOR_ALIASES[c]
    return None



def extract_shape(text: str):
    for s in SHAPE_ALIASES:
        if re.search(rf"\b{s}\b", text):
            return SHAPE_ALIASES[s]
    return None


def convert_value(value, unit):
    if value is None:
        return None, None
    if unit == "cm":
        return value / 100.0, "m"
    return value, unit


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
            cmd.error = "Distance invalide"
            return cmd

    if cmd.intent in {Intent.TOURNER_GAUCHE, Intent.TOURNER_DROITE}:
        if cmd.value is None:
            cmd.value = 90.0
        if cmd.unit is None:
            cmd.unit = "deg"

    if cmd.intent == Intent.DETECTER_COULEUR:
        if cmd.color is None:
            cmd.color = "ANY"

    cmd.valid = True
    return cmd


def parse_command(text: str) -> Command:
    norm = normalize_text(text)

    intent = detect_intent(norm)
    value, unit = extract_value_and_unit(norm)
    color = extract_color(norm)
    shape = extract_shape(norm)  

    cmd = Command(intent, value, unit, color, shape, text, norm)
    return validate_command(cmd)


def expand_special_intent(cmd: Command, repetitions: int = 6, step: float = 2):
    actions = []

    if cmd.intent == Intent.ZIGZAG:
        for i in range(repetitions):
            actions.append({
                "ok": True,
                "intent": Intent.AVANCER.value,
                "value": step,
                "unit": "m",
                "target_color": None,
                "target_shape": None  
            })
            actions.append({
                "ok": True,
                "intent": Intent.TOURNER_GAUCHE.value if i % 2 == 0 else Intent.TOURNER_DROITE.value,
                "value": 90.0,
                "unit": "deg",
                "target_color": None,
                "target_shape": None  
            })
    else:
        actions.append({
            "ok": True,
            "intent": cmd.intent.value,
            "value": cmd.value,
            "unit": cmd.unit,
            "target_color": cmd.color,
            "target_shape": cmd.shape  
        })

    return actions


def parse_to_robot_actions(text: str) -> List[dict]:
    normalized = normalize_text(text)
    parts = re.split(r"\b(?:puis|ensuite|et|then|and)\b|,", normalized)

    actions = []
    last_intent = None

    for part in parts:
        part = part.strip()
        if not part:
            continue

        cmd = parse_command(part)

        if cmd.intent in {Intent.ZIGZAG}:
            special_actions = expand_special_intent(cmd)
            actions.extend(special_actions)
            continue

        if cmd.intent == Intent.UNKNOWN and last_intent is not None:
            value, unit = extract_value_and_unit(part)

            cmd = Command(
                intent=last_intent,
                value=value,
                unit=unit,
                raw_text=part,
                normalized_text=part
            )
            cmd = validate_command(cmd)

        if cmd.valid:
            last_intent = cmd.intent
            actions.append({
                "ok": True,
                "intent": cmd.intent.value,
                "value": cmd.value,
                "unit": cmd.unit,
                "target_color": cmd.color,
                "target_shape": cmd.shape  
            })
        else:
            actions.append({
                "ok": False,
                "error": cmd.error,
                "raw": part
            })

    return actions

def execute_actions(actions):
    for action in actions:

        if not action["ok"]:
            print("Erreur:", action["error"])
            continue

        color = action.get("target_color")
        shape = action.get("target_shape")

        
        if color or shape:
            detection.track_object(color, shape)
            return





if __name__ == "__main__":
    print("Tape une commande ('quit' pour quitter)")
    while True:
        text = input(">> ")

        if text.lower() in {"quit", "exit"}:
            break

        payload = parse_to_robot_actions(text)
        print("Payload:", payload)

        execute_actions(payload)