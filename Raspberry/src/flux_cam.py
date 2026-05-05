import cv2 
import numpy as np
import sys


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    sys.stderr.write("Cannot open camera")
    exit()

while True:
   
    commande = sys.stdin.readline().strip()

    if commande == "scan":
        ret, img = cap.read()
        
        if not ret:
            sys.stderr.write("Erreur de reception de l'image")
            break
        params = [cv2.IMWRITE_JPEG_QUALITY, 50]
        cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        cv2.imwrite(r"C:\Users\kylia\Documents\Cours_UPS\PFR2\Interface\camera\image_cam.jpg", img, params)
        sys.stdout.write("image_OK")
        sys.stderr.write("[INFO] Image rafraichie")

        sys.stdout.flush()
        sys.stderr.flush()

cap.release()
cv2.destroyAllWindows()
