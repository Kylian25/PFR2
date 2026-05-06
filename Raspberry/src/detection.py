import time
import json

def tourner_gauche(angle):
    return [{'ok': True, 'intent': 'TOURNER_GAUCHE', 'value': angle, 'unit': 'deg', 'target_color': None, 'target_shape': None}]

def tourner_droite(angle):
    return [{'ok': True, 'intent': 'TOURNER_DROITE', 'value': angle, 'unit': 'deg', 'target_color': None, 'target_shape': None}]

def avancer(distance):
    return  [{'ok': True, 'intent': 'AVANCER', 'value': distance , 'unit': 'm', 'target_color': None, 'target_shape': None}]

def stop():
   return [{'ok': True, 'intent': 'STOP', 'value': None, 'unit': None, 'target_color': None, 'target_shape': None}]


def read_vision():
    try:
        with open(r"C:\Users\CMF5190A\Downloads\detections.json", "r") as f:
            return json.load(f)
    except:
        return []
    

def find_target(data, color=None, shape=None):
    for obj in data:
        if color and obj["couleur"].lower() != color:
            print(color) , print( obj["couleur"])
            continue
        if shape and obj["forme"] != shape:
            print(shape) , print( obj["forme"])
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
            tourner_droite(ROTATION_STEP)
            print(tourner_droite(ROTATION_STEP))
            rotations += 1

            if rotations >= MAX_ROTATIONS:
                print("Objet introuvable")
                stop()
                return

            time.sleep(0.3)
            continue

        rotations = 0
        

        position = target["position"]

       
        if position == "GAUCHE":
            tourner_gauche(10)
            print(tourner_gauche(10))
        elif position == "DROITE":
            tourner_droite(10)
            print(tourner_gauche(10))
            
        else: 
            avancer(0.2)


        avancer(10)

        time.sleep(0.1)