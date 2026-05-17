
# Manuel d'Utilisation — Robot Mobile
**Projet Fil Rouge 2 (PFR2) — UPSSITECH SRI**

---

## 1. Spécifications techniques & Architecture

### 1.1 Composants matériels principaux
* **Unité de calcul :** Raspberry Pi 3 B+ (Traitement d'images, Cartographie, Serveur Node-RED).
* **Contrôleur bas niveau :** Carte Arduino Mega + Shield moteur (Asservissement des moteurs, lecture des capteurs).
* **Vision :** Caméra Raspberry Pi (Pi Camera) montée sur un support imprimé en 3D.
* **Télémétrie & Cartographie :**
    * Capteur LiDAR RPLiDAR.
    * Deux capteurs ultrasons (un à l'avant, un sur le flanc droit).
* **Communication :** Module Bluetooth (liaison série pour application mobile) et liaison Série/USB entre le Raspberry Pi et l'Arduino.
<p align='center'>
  <img width="635" height="476" alt="robot_final" src="https://github.com/user-attachments/assets/0c58dc49-eb70-4dc1-b57e-e2949d54458c" />
</p>

---

## 2. Procédure de mise en route

Pour démarrer et initialiser correctement le robot, il faut suivre les étapes ci-dessous :

1. **Vérification mécanique :** Placez le robot sur une surface plane et assez dégagée.
2. **Mise sous tension des moteurs :** Branchez l'alimentation principale à la batterie des moteurs (châssis).
3. **Démarrage du système :** Connectez le câble d'alimentation micro-USB de la batterie externe au Raspberry Pi. Les LED du Pi doivent s'allumer.
4. **Initialisation du LiDAR :** Au démarrage, le moteur du LiDAR va s'allumer et attendre la première commande de scan.

---

## 3. Accès à l'interface utilisateur (Node-RED)

L'interface de contrôle contenant la télémétrie, le retour vidéo, les logs et la cartographie est sur un serveur Node-RED s'exécutant sur le Raspberry Pi.

### 3.1 Lancement du serveur Node-RED
Si le serveur ne démarre pas automatiquement au boot du Raspberry Pi, connectez-vous en SSH ou ouvrez un terminal local et saisissez :

```bash
node-red-start
```
### 3.2 Connexion à l'interface web
1. Connectez votre ordinateur au même réseau Wi-Fi que le Raspberry Pi.
2. Ouvrez votre navigateur internet.
3. Saisissez l'adresse de l'interface en remplaçant IP_pi par l'adresse IP réelle du robot:
```text
   http://IP_pi:1880
```

<p align='center'>
<img width="1324" height="637" alt="Capture d&#39;écran 2026-05-12 141554" src="https://github.com/user-attachments/assets/7f67cd1d-872b-4d41-b3fd-facddd412de4" />
</p>

---

## 4. Guide des modes de pilotage

Le robot possède 3 modes de fonctionnement différents (manuel, automatique, requêtes) sélectionnables depuis les boutons présents sur l'interface.

### 4.1 Mode Manuel (Contrôle Bluetooth sur Smartphone)
Ce mode permet le pilotage direct du robot à l'aide d'une manette virtuelle sur une application de téléphone portable via le Bluetooth.

* **Connexion :** Activez le Bluetooth sur votre smartphone, recherchez le module du robot et effectuez l'appairage.
* **Contrôle :** Utilisez les boutons de l'application pour déplacer le robot : avancer, reculer, tourner à gauche ou tourner à droite.
* **Sécurité anti-collision active :** Si le capteur ultrason avant détecte un obstacle, l'appui sur la touche pour avancer ne fera pas avancer le robot afin d'éviter les collisions.
* **Bascule rapide :** Vous pouvez basculer instantanément du mode manuel au mode automatique en pressant la touche "w" de l'application.

### 4.2 Mode Automatique (Évitement d'obstacles autonome)
En mode automatique, le robot navigue de manière autonome en détectant son environnement.

1. Au passage en mode automatique, le robot avance tout droit jusqu'à ce que le capteur ultrason frontal détecte un obstacle.
2. Il tourne alors à gauche jusqu'à ce que l'obstacle soit détecté par le capteur ultrason situé à droite.
3. Une fois l'obstacle localisé sur son flanc droit, le robot avance de nouveau tout droit jusqu'à détecter un nouvel obstacle.

### 4.3 Mode Requêtes (Traitement du Langage Naturel)
Le mode requêtes permet d'envoyer des instructions complexes en langage naturel, en anglais ou en français, par écrit ou par commande vocale.

#### A. Saisie textuelle ou vocale
* **Requête écrite :** Saisissez votre texte dans la barre dédiée de l'interface.
* **Requête vocale :**
    1. Dans le menu déroulant de la partie requête de l'interface, sélectionnez la langue que vous souhaitez utiliser.
    2. Lancez le script Python de reconnaissance vocale via le micro (sur votre ordinateur).
    3. Énoncez clairement la commande (ex: "avance de 3m puis tourne à gauche puis tournez à droite").

#### B. Syntaxe supportée (Exemples de commandes)
Le système s'appuie sur une structure de dictionnaire bilingue pour les mots-clés:

* **AVANCER :** Exemples acceptés : "avance", "va tout droit" (FR) / "forward" (EN). Paramètres : Valeur numérique et unité.
* **TOURNER_GAUCHE :** Exemples acceptés : "tourne à gauche" (FR) / "turn left" (EN). Paramètres : Valeur numérique et unité.
* **TOURNER_DROITE :** Exemples acceptés : "tourne à droite" (FR) / "turn right" (EN). Paramètres : Valeur numérique et unité.
* **ZIGZAG :** Exemples acceptés : "faites des zigzag" (FR) / "zigzag" (EN). Paramètres : Aucun.
* **DETECTER_COULEUR :** Exemples acceptés : "cherche la balle rouge" (FR) / "find the red ball" (EN). Paramètres : Couleur (rouge, vert, bleu).

*Note sur la gestion du contexte :* Si vous oubliez le verbe d'action dans une sous-commande (ex: "Avance de 1 m puis de 2m"), le module récupère la dernière intention valide connue : 
```json
[{"ok": true, "intent": "AVANCER", "value": 1.0, "unit": "m", "target_color": null, "target_shape": null}]
[{"ok": true, "intent": "AVANCER", "value": 2.0, "unit": "m", "target_color": null, "target_shape": null}]
```

#### C. Comportement face aux obstacles durant les séquences
Si le robot rencontre un obstacle pendant l'exécution d'un enchaînement de requêtes ou d'une requête complexe (par exemple : zigzag):
1. Le robot s'arrête et interrompt la commande en cours.
2. Il passe automatiquement à la commande suivante de la séquence (ce qui n'est pas idéal dans les cas ou le robot devrait abandonner toutes les commandes suivantes).

---

## 5. Fonctionnalités avancées

### 5.1 Asservissement visuel (Suivi de cible de couleur)
Le robot est capable de repérer une balle de couleur rouge, verte ou bleue dans son champ de vision, de déterminer sa position spatiale et d'assurer un guidage autonome.

#### A. Calibration de la caméra
Le flux vidéo est acquis en temps réel via la bibliothèque Pi Camera 2 avec une résolution retenue de 320x240 pixels. Pour obtenir la meilleure détection :
1. Évitez les fortes variations de luminosité qui influencent la perception des couleurs et provoquent des faux positifs.
2. L'image est convertie dans l'espace HSV pour isoler les régions à l'aide des masques binaires.

<p align='center'>
  <img width="628" height="479" alt="camera" src="https://github.com/user-attachments/assets/4ee5e473-5d76-4318-abb2-d49e088d95c2" />
</p>

#### B. Cycle d'alignement autonome (track_object)
Lorsque l'intention de détection visuelle est activée:
1. **Phase de Recherche Active :** Si la cible n'est pas détectée, le robot pivote sur lui-même par pas réguliers de 20 degrés. Si le robot effectue plus de 360 degrés sans trouver la cible, il génère une commande d'arrêt pour éviter une boucle infinie.
2. **Phase de Centrage :** Dès que la cible est identifiée, le système évalue sa position relative selon trois zones horizontales:
    * **0% à 33% de la largeur :** Zone gauche -> Le robot applique des micro-rotations de 10 degrés pour corriger l'angle.
    * **66% à 100% de la largeur :** Zone droite -> Le robot applique des micro-rotations de 10 degrés vers la droite.
    * **33% à 66% de la largeur :** Zone centre -> La cible est centrée.
3. **Approche :** Dès que l'objet est centré, le robot valide la commande de déplacement final (avancer vers l'objet) puis s'arrête.
<p align="center">
   <img width="600" height="425" alt="recherche_balle" src="https://github.com/user-attachments/assets/bb165e4d-1671-4a8e-a9d3-97e70b3c279e" />
</p>

### 5.2 Cartographie LiDAR
Pour cartographier la pièce (murs, obstacles) et afficher un nuage de points sur l'interface utilisateur:

1. Appuyez sur le bouton "Rafraichir Lidar" via l'interface Node-RED ou attendez qu'il le fasse automatiquement (environ toutes les 10 secondes).
2. Les fonctions du script Python récupèrent les données brutes sous forme de tuple (qualité, angle, distance) selon le nombre de tours souhaité.
3. Les coordonnées cartésiennes (x, y) nécessaires à l'affichage sont calculées à partir des distances et des angles avant enregistrement.
4. La carte sous forme de nuage de points s'affiche sur l'interface graphique.
<p align='center'>
  <img width="623" height="398" alt="lidar_scan" src="https://github.com/user-attachments/assets/d4f02d53-a360-4c73-b6fd-ef5f0f497f84" />

</p>

---

## 6. Maintenance & dépannage

### 6.1 Accès aux données système
Le robot enregistre ses informations d'état au format JSON dans le dossier data. Vous pouvez regarder ces fichiers pour le diagnostic :

* **Fichier de télémétrie (telemetrie.json) :** Permet de vérifier l'état des capteurs et le mode actif.
* **Fichier de vision (detections.json) :** Interface d'échange contenant le résultat du traitement d'image.
* **Fichier image (image_detectee.jpg) :** Image sauvegardée automatiquement correspondant à la dernière scène détectée.

### 6.2 Résolution des problèmes fréquents

* **Problème : Le retour caméra sur l'interface Node-RED reste figé.**
    * *Solution :* Pressez le bouton "Récupérer img" (bloc gris via l'éditeur de noeuds) qui envoi l'ordre de capture en entrée du nœud. Le bloc IMAGE CAM est un nœud Daemon qui relance automatiquement le script camera.py en arrière-plan en cas d'erreur.
* **Problème : Erreur de communication ou mauvais format détecté.**
    * *Solution :* Ouvrez la console de débogage Node-RED reliée aux blocs verts (debug) pour analyser les sorties stdout et stderr des scripts. Les erreurs de communication série ou les lignes défaillantes sont également redirigées vers un fichier de logs dédié (logs.txt).
* **Problème : Détection d'objets parasites en arrière-plan.**
    * *Solution :* Si des pixels de l'environnement partagent une teinte trop proche des balles cibles, nettoyez l'image en adaptant les seuils HSV ou modifiez le filtrage basé sur l'aire des contours (aire configurée entre 300 et 30000 pixels).


