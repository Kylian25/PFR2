import serial
import time
import sys
import threading

# --- CONFIGURATION DU PORT ---
if sys.platform.startswith('win'):
    port_nom = 'COM3' 
else:
    port_nom = '/dev/ttyACM0'

try:
    ser = serial.Serial(port_nom, 38400, timeout=0.1)
    time.sleep(2) 
    print(f"Connecté à l'Arduino sur {port_nom}")
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
                sys.stdout.write("Entrez une commande : ")
                sys.stdout.flush()
            except:
                pass
        time.sleep(0.01)

thread_lecture = threading.Thread(target=lecture_continue, daemon=True)
thread_lecture.start()

# --- BOUCLE PRINCIPALE ---
try:
    while True:
        cmd = input()
        if cmd:
            ser.write(cmd.encode('utf-8'))
except KeyboardInterrupt:
    print("\nFermeture...")
finally:
    ser.close()