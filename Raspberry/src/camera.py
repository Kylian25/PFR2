from picamera2 import Picamera2
import cv2
import numpy as np
import json
import os
os.environ['LIBCAMERA_LOG_LEVELS'] = 'FATAL'
import sys

# ================= POSITION =================
def get_position(x, w, frame_width):

    center_x = x + w // 2

    norm_x = center_x / float(frame_width)

    if norm_x < 0.33:
        return "GAUCHE"

    elif norm_x > 0.66:
        return "DROITE"

    else:
        return "CENTRE"


# ================= DETECTION =================
def detect_balls(frame):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    detections = []

    # ================= ROUGE =================
    lower_red1 = np.array([0, 150, 100])
    upper_red1 = np.array([8, 255, 255])

    lower_red2 = np.array([170, 150, 100])
    upper_red2 = np.array([180, 255, 255])

    mask_red = cv2.inRange(hsv,
                           lower_red1,
                           upper_red1) + \
               cv2.inRange(hsv,
                           lower_red2,
                           upper_red2)

    # ================= VERT =================
    lower_green = np.array([45, 120, 80])
    upper_green = np.array([80, 255, 255])

    mask_green = cv2.inRange(hsv,
                             lower_green,
                             upper_green)

    # ================= BLEU =================
    lower_blue = np.array([100, 170, 80])
    upper_blue = np.array([125, 255, 255])

    mask_blue = cv2.inRange(hsv,
                            lower_blue,
                            upper_blue)

    masks = {
        "ROUGE": mask_red,
        "VERT": mask_green,
        "BLEU": mask_blue
    }

    colors_draw = {
        "ROUGE": (0, 0, 255),
        "VERT": (0, 255, 0),
        "BLEU": (255, 0, 0)
    }

    kernel = np.ones((3,3), np.uint8)

    # ================= DETECTION =================
    for color_name, mask in masks.items():

        # nettoyage léger
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(mask,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:

            area = cv2.contourArea(cnt)

            # filtre taille
            if area < 300 or area > 50000:
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            # filtre balle uniquement
            ratio = w / float(h)

            if ratio < 0.75 or ratio > 1.25:
                continue

            center_x = x + w // 2
            center_y = y + h // 2

            position = get_position(x,
                                    w,
                                    frame.shape[1])

            # stockage JSON
            detections.append({
                "couleur": color_name,
                "position": position,
                "centre": [center_x, center_y]
            })

            # rectangle
            cv2.rectangle(frame,
                          (x, y),
                          (x + w, y + h),
                          colors_draw[color_name],
                          2)

            # texte
            cv2.putText(frame,
                        f"{color_name} - {position}",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        colors_draw[color_name],
                        2)

            # coordonnées
            cv2.putText(frame,
                        f"({center_x},{center_y})",
                        (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255,255,255),
                        2)

    return frame, detections


# ================= CAMERA =================
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (640, 480)}
)

picam2.configure(config)

picam2.start()


# ================= BOUCLE =================
while True:
    
    commande = sys.stdin.readline().strip()

    if commande == "image":

        try:

            frame = picam2.capture_array()

            frame = cv2.cvtColor(frame,
                                cv2.COLOR_RGB2BGR)

            frame, detections = detect_balls(frame)

            # ================= JSON =================
            with open("/home/groupe2sri/PFR2/Raspberry/data/detections.json", "w") as f:
                json.dump(detections,f,indent=4)

            # ================= CAPTURE IMAGE =================
            #if detections:

            image_name = "/home/groupe2sri/PFR2/Raspberry/data/derniere_image.jpg"

            cv2.imwrite(image_name, frame)
            sys.stdout.write("image_OK\n")
            sys.stdout.flush()

        except Exception as e:
            print(f"[ERREUR][LIDAR] : {e}")


