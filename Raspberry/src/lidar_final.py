from rplidar import RPLidar
import time
import numpy as np
import json
import sys

##################  Initialisation lidar ######################
lidar = RPLidar('/dev/ttyUSB0')
try:
    lidar.stop()
    lidar.reset()
    time.sleep(1)
except:
    pass

###################### Fonctions ##############################
def recup_donnes_lidar_tours(lidar, nb_tours):
    lidar.clean_input()
    
    data = []
    try:
        count = 0
        for scan in lidar.iter_scans(max_buf_meas=5000):
            count += 1
            if count <= 2: 
                continue
            
            data.append(scan)
            if len(data) >= nb_tours:
                break
    except Exception as e:
        raise e
        
    return data


def scans_2_list(data):
    res=[]
    for scan in data:
        for point in scan:
            res.append(point)
    return res

#######################   Main     ############################

try:
    print("[LIDAR] Démarrage du moteur", file=sys.stderr, flush=True)
    lidar.start_motor()
    time.sleep(2)
    
    while True:
        commande = sys.stdin.readline().strip()

        if not commande:
            continue

        if commande == "scan":
            print("[LIDAR] Commande scan recue", file=sys.stderr, flush=True)
            try:
                data_tours = recup_donnes_lidar_tours(lidar, 5)
                points = scans_2_list(data_tours)

                res = []
                for p in points:
                    angle_rad = np.radians(p[1])
                    dist_m = p[2] / 1000.0
                    
                    if dist_m > 0:
                        res.append({
                            "x" : round(dist_m * np.cos(angle_rad), 3),
                            "y" : round(dist_m * np.sin(angle_rad), 3),
                            "dist" : round(dist_m, 3),
                            "angle" : round(p[1], 3)
                        })

                with open("/home/groupe2sri/PFR2/Raspberry/data/lidar_scan.json", "w") as f:
                    json.dump(res, f, indent=4)
                
                print("SCAN_OK", flush=True)

            except Exception as e:
                print(f"[ERREUR][LIDAR] {e}", file=sys.stderr, flush=True)
                lidar.reset()
                time.sleep(2)
                lidar.start_motor()
                time.sleep(1)

        if commande in ["quit", "exit"]:
            break

except KeyboardInterrupt:
    print("[LIDAR] Arrêt", file=sys.stderr, flush=True)
finally:
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()