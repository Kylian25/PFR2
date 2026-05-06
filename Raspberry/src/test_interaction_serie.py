import serial
import time
import sys
import threading
import json
import reconnaissance_texte_2_nonterminé as text



# --- CONFIGURATION DU PORT ---
if sys.platform.startswith('win'):
    port_nom = 'COM3' 
else:
    port_nom = '/dev/ttyACM0'

try:
    ser = serial.Serial(port_nom, 38400, timeout=0.1)
    time.sleep(2)
    ser.reset_input_buffer()
    ser.write(b'r')
    print(f"Connecté et mode requêtes activé sur {port_nom}")
except Exception as e:
    print(f"Erreur : {e}")
    sys.exit()

robot_occupe = threading.Event()
FICHIER_STATUT = "C:\\Users\grums\Documents\Cours_3A_SRI\PFR\dépot_git_PFR2\PFR2\Raspberry\data\\telemetrie.json"

def mettre_a_jour_json(obs_fwd, obs_right, speed):
    data = {
        "obstacle_devant": int(obs_fwd),
        "obstacle_droite": int(obs_right),
        "vitesse_actuelle": int(speed)
    }
    with open(FICHIER_STATUT, 'w') as f:
        json.dump(data, f, indent=3)

# --- LECTURE  ---
def lecture_continue():
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.startswith("TELEMETRIE:"):
                    valeurs = line.replace("TELEMETRIE:", "").split(",")
                    if len(valeurs) == 3:
                        mettre_a_jour_json(valeurs[0], valeurs[1], valeurs[2])

                elif "ALERTE_OBSTACLE" in line:
                    sys.stdout.write('\r' + ' ' * 60 + '\r')
                    print("\n[!] ARRÊT D'URGENCE : Obstacle détecté pendant la séquence !")
                
                else:
                    sys.stdout.write('\r' + ' ' * 60 + '\r') 
                    print(f"Réponse: {line}")
                    if "SEQUENCE_TERMINEE" in line:
                        robot_occupe.set()
                    sys.stdout.write("> ")
                    sys.stdout.flush()
            except Exception as e:
                print(f"Erreur lecture: {e}")
        time.sleep(0.01)

thread_lecture = threading.Thread(target=lecture_continue, daemon=True)
thread_lecture.start()

def envoyer_sequence_dictionnaires(liste_commandes):
    elements = [f"{d['intent']},{d['value']}" for d in liste_commandes if d['ok']]
    if elements:
        payload = " ".join(elements) + "\n"
        robot_occupe.clear()
        
        ser.write(payload.encode('utf-8'))
        print(f"Envoyé : {payload.strip()}")
        
        print("En attente de la fin de la séquence...")
        robot_occupe.wait()
        print("Séquence terminée ! Retour au menu.")

# --- BOUCLE PRINCIPALE ---
try:
    while True:
        print("\n--- Menu ---")
        print("1. Passer en mode Requêtes ('r')")
        print("2. Envoyer séquence test (Dictionnaires)")
        print("A. Passer en mode Automatique ('A')")
        print("W. Passer en mode Manuel ('w')")
        
        choix = input("Votre choix : ").strip()

        if choix == '1':
            ser.write(b'r')
            print("\n-> Ordre envoyé : Mode Requêtes")
            cmd = input("Entrez la commande : ")
            cmd = text.parse_to_robot_actions(cmd)
            if cmd:
                envoyer_sequence_dictionnaires(cmd)
        
        elif choix == '2':
            ma_liste = [
                {"ok": True, "intent": "AVANCER", "value": 2},
                {"ok": True, "intent": "TOURNER", "value": 90},
                {"ok": False, "intent": "STOP", "value": 0}
            ]
            envoyer_sequence_dictionnaires(ma_liste)
            
        elif choix.upper() == 'A':
            ser.write(b'@')
            print("\n-> Ordre envoyé : Mode Automatique")
            
        elif choix.upper() == 'W':
            ser.write(b'w')
            print("\n-> Ordre envoyé : Mode Manuel")

except KeyboardInterrupt:
    print("\nFermeture...")
finally:
    ser.close()