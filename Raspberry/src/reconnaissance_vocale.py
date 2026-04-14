""" Ce fichier contient le programme permettant d'utiliser la commande vocale
Nom du développeur : Charles MARDON
Date de la version : 25 janvier 2026
"""

import sys
import speech_recognition as sr
import reconnaissance_texte as rte


def commande_vocale(langue):
    r = sr.Recognizer()
    micro = sr.Microphone()

    with micro as source:
        print("Speak!")
        audio_data = r.listen(source)
        print("End!")

    if langue == "FR":
        result = r.recognize_google(audio_data, language="fr-FR")
    else:
        result = r.recognize_google(audio_data, language="en-EN")

    return result


def sauvegarder_texte(resultat):
    with open(r"C:\Users\CMF5190A\Downloads\rect.txt", "w", encoding="utf-8") as fichier:
        fichier.write(resultat)


def test_text():
    with open(r"C:\Users\CMF5190A\Downloads\rect.txt", "r", encoding="utf-8") as fichier:
        texte = fichier.read().strip()

    cmd = rte.parse_command(texte)
    payload = rte.command_to_robot_payload(cmd)

    print("Texte lu :", texte)
    print("Parsed :", cmd)
    print("Payload :", payload)
    print("-" * 40)


if __name__ == "__main__":
    result = commande_vocale(sys.argv[1])
    sauvegarder_texte(result)
    test_text()