""" Ce fichier contient le programme permettant d'utiliser la commande vocale 
Nom du développeur : Charles MARDON
Date de la version : 25 janvier 2026
"""

from gtts import gTTS
import sys
import speech_recognition as sr


def commande_vocale(langue):
    r = sr.Recognizer()
    micro = sr.Microphone()
    with micro as source:
        print("Speak!")
        audio_data = r.listen(source)
        print("End!")

    if (langue == "FR"):
        result = r.recognize_google(audio_data, language="fr-FR")
    else:
        result = r.recognize_google(audio_data, language="en-EN")
    return result

# Programme principal


result = commande_vocale(sys.argv[1])

with open(r"C:\Users\ntech\Downloads\reconaissance.txt", "w", encoding="utf-8") as fichier:
    fichier.write(result)
