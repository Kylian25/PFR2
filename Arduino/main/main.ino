#include "automatique.h"

AF_DCMotor motor1(1); // ARR Gauche
AF_DCMotor motor2(2); // AV Gauche
AF_DCMotor motor3(3); // ARR Droit
AF_DCMotor motor4(4); // AV Droit

const int trig_fwd = 30;
const int echo_fwd = 31;
const int trig_right = 40;
const int echo_right = 41;

#define V_DROIT 170
#define V_TURN 230

int etat_present = 0;
int etat_suivant = 0;
int mode = 1;
unsigned long dernierEnvoi = 0;
const int intervalle = 500;
unsigned long finActionMillis = 0;
bool actionEnCours = false;
char dernierOrdre = 'S';

void setup() {
  Serial.begin(38400); 
  Serial3.begin(38400);
  Serial.setTimeout(10);
  
  motor1.setSpeed(V_DROIT); 
  motor2.setSpeed(V_DROIT);
  motor3.setSpeed(V_DROIT);
  motor4.setSpeed(V_DROIT); 

  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);

  pinMode(trig_fwd,OUTPUT);
  pinMode(echo_fwd,INPUT);
  pinMode(trig_right,OUTPUT);
  pinMode(echo_right,INPUT);

  while(Serial.available() > 0) Serial.read();
  while(Serial3.available() > 0) Serial3.read();
}

void loop() {
  // --- GESTION DES COMMANDES (SERIAL & SERIAL3) ---
  if (Serial.available() > 0 || Serial3.available() > 0) {
    // On récupère le caractère, peu importe d'où il vient
    char c;
    if (Serial.available() > 0) c = Serial.read();
    else c = Serial3.read();

    // --- LOGIQUE DE CHANGEMENT DE MODE (PRIORITAIRE) ---
    if (c == '@' || c == 'W') { // 'A' pour Auto, 'W' pour Auto via Serial3
      mode = 0;
      Serial.println("Passage en mode automatique");
    }
    else if (c == 'w') { // 'w' pour Manuel
      mode = 1;
      stopMoteurs();
      Serial.println("Passage en mode manuel");
    }
    else if (c == 'r') { // 'r' pour Requêtes
      mode = 2;
      stopMoteurs();
      Serial.println("Passage en mode requetes");
    }
    // --- LOGIQUE SPECIFIQUE AUX MODES ---
    else {
      if (mode == 1) {
        mode_manuel(c, trig_fwd, echo_fwd);
      }
      else if (mode == 2) {
        // Si on est en mode 2 et que ce n'est pas un changement de mode, 
        // c'est le début d'une chaîne de caractères (String)
        // On reconstruit la String à partir du premier caractère déjà lu 'c'
        String commande = String(c) + Serial.readStringUntil('\n');
        mode_requetes(commande);
        while(Serial.available() > 0) Serial.read(); // Vidage
      }
    }
  }

  // --- EXECUTION DES MODES ---
  if (mode == 0) {
    mode_auto(trig_fwd, echo_fwd, trig_right, echo_right);
  }
  
  if (mode == 2 && actionEnCours) {
    if (millis() >= finActionMillis) {
      stopMoteurs();
      actionEnCours = false;
    }
  }
}
