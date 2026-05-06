import cv2 
import numpy as np
import sys
from picamera2 import Picamera2


picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

try:
    while True:
        
        commande = sys.stdin.readline().strip()

        if commande == "image":
            
            img = picam2.capture_array()
            
            if img is None:
                sys.stderr.write("Erreur de réception de l'image\n")
                continue

           
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
         
            path = "/home/groupe2sri/PFR2/Raspberry/data/derniere_image.jpg"
            params = [cv2.IMWRITE_JPEG_QUALITY, 50]
            cv2.imwrite(path, img_gray, params)
            
            
            sys.stdout.write("image_OK\n")
            sys.stderr.write("[INFO] Image rafraîchie\n")

            sys.stdout.flush()
            sys.stderr.flush()

except Exception as e:
    sys.stderr.write(f"Erreur fatale : {e}\n")
finally:
    picam2.stop()
    cv2.destroyAllWindows()