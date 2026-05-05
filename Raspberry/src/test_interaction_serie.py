import serial
import time
import sys
import threading
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

# --- LECTURE  ---
def lecture_continue():
    while True:
        if ser.in_waiting > 500: 
            ser.reset_input_buffer()
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                sys.stdout.write('\r' + ' ' * 60 + '\r') 
                print(f"Réponse: {line}")
                sys.stdout.write("> ")
                sys.stdout.flush()
            except:
                pass
        time.sleep(0.01)

thread_lecture = threading.Thread(target=lecture_continue, daemon=True)
thread_lecture.start()

def envoyer_sequence_dictionnaires(liste_commandes):
    elements = [f"{d['intent']},{d['value']}" for d in liste_commandes if d['ok']]
    if elements:
        payload = " ".join(elements) + "\n"
        ser.write(payload.encode('utf-8'))
        print(f"Envoyé : {payload.strip()}")

# --- BOUCLE PRINCIPALE ---
try:
    while True:
        print("\n--- Menu ---")
        print("1. Passer en mode Requêtes ('r')")
        print("2. Envoyer séquence test (Dictionnaires)")
        print("A. Passer en mode Automatique ('A')")
        print("W. Passer en mode Manuel ('w')")
        
        # On supprime les espaces inutiles avec .strip()
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