from rplidar import RPLidar
import time
import numpy as np
import json
import sys

##################  Initialisation lidar ######################
lidar = RPLidar('/dev/ttyUSB0')
lidar.stop()
time.sleep(0.5)
lidar.reset()
time.sleep(1)
lidar.start_motor()
lidar.clean_input()

###################### Fonctions ##############################

def recup_donnes_lidar_tours(lidar, nb_tours):

    time.sleep(0.1)
    lidar.clean_input()
    try:
        data = []
        scans = lidar.iter_scans('normal', 3000, 200)

        for scan in scans:
            data.append(scan)
            if len(data)>nb_tours:
                break
    finally:
        lidar.stop()
        time.sleep(0.1)
        lidar.clean_input()

    return data

def scans_2_list(data):
    res=[]
    for scan in range(len(data)):
        for point in range(len(data[scan])):
            res.append(data[scan][point])
    return res


#######################   Main     ############################

while True:

    commande = sys.stdin.readline().strip()

    if commande == "scan":
        
        ###### test
        print("[LIDAR] Commande scan recue", file=sys.stderr, flush=True)
        #######
        try:
            lidar.start_motor()

            res=[]
            data_tours = recup_donnes_lidar_tours(lidar, 5)
            points = scans_2_list(data_tours)

            for p in points:
                x=round(p[2]/1000*np.cos(np.radians(p[1])),3)
                y=round(p[2]/1000*np.sin(np.radians(p[1])),3)
                res.append({"x" : x,
                            "y" : y,
                            "dist" : round(p[2]/1000,3),
                            "angle" : round(p[1],3)})

            with open("/home/groupe2sri/PFR2/Raspberry/data/lidar_scan.json", "w") as f:
                json.dump(res, f, indent=4)
            print("SCAN_OK", flush=True)

        except Exception as e:
            print(f"[ERREUR][LIDAR] {e}", file=sys.stderr, flush=True)
            lidar.reset()
            time.sleep(0.5)


