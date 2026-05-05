from rplidar import RPLidar
import time
import numpy as np
import json
import sys

##################  Initialisation lidar ######################
time.sleep(1)
lidar = RPLidar('COM4')
lidar.reset()
lidar.start_motor()
lidar.clean_input()

###################### Fonctions ##############################

def recup_donnes_lidar_tours(lidar, nb_tours):

    time.sleep(1)
    lidar.clean_input()
    data = []
    scans = lidar.iter_scans('normal', 5000, 200)

    for scan in scans:
        data.append(scan)
        if len(data)>nb_tours:
            break

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
        
        res=[]
        data_tours = recup_donnes_lidar_tours(lidar, 3)
        points = scans_2_list(data_tours)

        for p in points:
            x=round(p[2]/1000*np.cos(np.radians(p[1])),3)
            y=round(p[2]/1000*np.sin(np.radians(p[1])),3)
            res.append({"x" : x,
                        "y" : y,
                        "dist" : round(p[2]/1000,3),
                        "angle" : round(p[1],3)})

        with open(r"C:\Users\kylia\Documents\Cours_UPS\PFR2\Interface\lidar_scan.json", "w") as f:
            json.dump(res, f, indent=4)


