import time
import json

def tourner_gauche(angle):
    return [{'ok': True, 'intent': 'TOURNER_GAUCHE', 'value': angle, 'unit': 'deg', 'target_color': None, 'target_shape': None}]

def tourner_droite(angle):
    return [{'ok': True, 'intent': 'TOURNER_DROITE', 'value': angle, 'unit': 'deg', 'target_color': None, 'target_shape': None}]

def avancer(distance):
    return [{'ok': True, 'intent': 'AVANCER', 'value': distance , 'unit': 'm', 'target_color': None, 'target_shape': None}]

def stop():
   return [{'ok': True, 'intent': 'STOP', 'value': None, 'unit': None, 'target_color': None, 'target_shape': None}]


def read_vision():
    try:
        with open(r"C:\Users\grums\Documents\Cours_3A_SRI\PFR\dépot_git_PFR2\PFR2\Raspberry\src\detections.json", "r") as f:
            return json.load(f)
    except Exception as e:
        return []
    

def find_target(data, color=None, shape=None):
    
    traductions_fr = {
        "red": "rouge", "green": "vert", "blue": "bleu", 
        "yellow": "jaune", "black": "noir", "white": "blanc",
        "pink": "rose", "purple": "violet", "orange": "orange"
    }
    
    color_fr = traductions_fr.get(color, color) if color else None

    for obj in data:
        if color_fr and obj.get("couleur", "").lower() != color_fr:
            continue
        if shape and obj.get("forme") != shape:
            continue
        return obj
    return None


def track_object(target_color=None, target_shape=None):
    MAX_ROTATIONS = 12
    ROTATION_STEP = 30
    rotations = 0

    while True:
        data = read_vision()
        target = find_target(data, target_color, target_shape)

        if not target:
            yield tourner_droite(ROTATION_STEP)
            rotations += 1

            if rotations >= MAX_ROTATIONS:
                yield stop()
                break 

            time.sleep(0.3)
            continue
        else:
            rotations = 0
            position = target.get("position", "CENTRE") 

            if position == "GAUCHE":
                yield tourner_gauche(10)
            elif position == "DROITE":
                yield tourner_droite(10) 
            else: 
                yield avancer(20)
                yield stop()
                break 

        time.sleep(0.5)