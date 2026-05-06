
import sys
import speech_recognition as sr
import reconnaissance_texte as rte
import requests

PI_URL = "http://localhost:1880"
#PI_URL = "http://192.168.1.XX:1880"


def commande_vocale(langue):
    r = sr.Recognizer()
    
    try:
        #device_index=17
        micro = sr.Microphone()

        with micro as source:
            print(f"Langue : {langue}")
            print("Speak!")
            audio_data = r.listen(source,timeout=5)
            print("End!")

            if langue == "FR":
                result = r.recognize_google(audio_data, language="fr-FR")
            else:
                result = r.recognize_google(audio_data, language="en-EN")

            print(f"{result}")
            response = requests.post(f"{PI_URL}/robot/commande", data=result.encode('utf-8'))

            if response.status_code == 200:
                print("[PC] Commande envoyée" \
                    " ")
            else:
                print(f"[ERREUR] La Pi a répondu : {response.status_code}")


    except sr.UnknownValueError:
        print("[PC] Audio impossible à traiter")
    except sr.RequestError as e:
        print(f"[PC] Erreur service recognition : {e}")
    except Exception as e:
        print(f"[PC] Erreur connexion Pi : {e}")

def obtenir_langue_depuis_pi():
    try:
        reponse = requests.get(f"{PI_URL}/robot/langue", timeout=1)
        if reponse.status_code == 200:
            print("reponse langue Pi : OK")
            return reponse.text 
    except:
        print("Impossible d'obtenir la langue, langue par défaut : FR")
    return "FR"
    

if __name__ == "__main__":
    while True:
        input("Appuyez sur ENTRÉE pour donner un ordre au robot (Ctrl+C pour quitter)")
        langue=obtenir_langue_depuis_pi()
        print(langue)
        commande_vocale(langue)