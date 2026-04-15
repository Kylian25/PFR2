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

  // NETTOYAGE DU TAMPON AU DÉMARRAGE
  while(Serial.available() > 0) Serial.read();
  while(Serial3.available() > 0) Serial3.read();
}

void loop() {
  if (mode != 2 && Serial.available() > 0) {
    char bouton = Serial.read();

    if (bouton == 'A') {
      mode = 0;
      Serial.println("Passage en mode automatique");
    }
    else if (bouton == 'r') {
      mode = 2;
      stopMoteurs();
      Serial.println("Passage en mode requêtes");
    }
    else if (mode == 1) mode_manuel(bouton, trig_fwd, echo_fwd);
  }

  if (Serial3.available() > 0) {
    char bouton3 = Serial3.read();
    
    if (bouton3 == 'W') {
      mode = 0;
      Serial.println("Passage en mode automatique");
    }
    else if (bouton3 == 'w') {
      mode = 1;
      stopMoteurs();
      Serial.println("Passage en mode manuel");
    }
    else if (mode == 1) mode_manuel(bouton3, trig_fwd, echo_fwd);
  }

  if (mode == 0) mode_auto(trig_fwd, echo_fwd, trig_right, echo_right);
  else if (mode == 2) {
    if (Serial.available() > 0) {
      if (Serial.peek() == 'w') { 
        mode = 1; 
        Serial.read(); 
        Serial.println("Retour Manuel");
      }
      else {
        String commande = Serial.readStringUntil('\n');
        mode_requetes(commande);
        while(Serial.available() > 0) { Serial.read(); }
      }
    }
  }
}
