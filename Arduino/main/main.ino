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
int mode = 2;
unsigned long dernierEnvoi = 0;
const int intervalle = 500;
unsigned long finActionMillis = 0;
bool actionEnCours = false;
char dernierOrdre = 'S';

struct Action {
  char intention[20];
  int valeur;
};

#define MAX_ACTIONS 15
Action fileActions[MAX_ACTIONS];
int totalActions = 0;
int actionCouranteIndex = 0;

int obs_fwd = 0;
int obs_right = 0;
int v_actuelle = 0;
unsigned long dernierEnvoiTelemetrie = 0;
const int intervalleTelemetrie = 200;

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
  if (Serial.available() > 0 || Serial3.available() > 0) {
    char c;
    if (Serial.available() > 0) c = Serial.read();
    else c = Serial3.read();

    if (c == '@' || c == 'W') {
      mode = 0;
      Serial.println("Passage en mode automatique");
    }
    else if (c == 'w') {
      mode = 1;
      stopMoteurs();
      Serial.println("Passage en mode manuel");
    }
    else if (c == 'r') {
      mode = 2;
      stopMoteurs();
      Serial.println("Passage en mode requetes");
    }
    else {
      if (mode == 1) {
        mode_manuel(c, trig_fwd, echo_fwd);
      }
      else if (mode == 2) {
        String commande = String(c) + Serial.readStringUntil('\n');
        mode_requetes(commande);
        while(Serial.available() > 0) Serial.read();
      }
    }
  }

  if (mode == 0) {
    mode_auto(trig_fwd, echo_fwd, trig_right, echo_right);
  }
  
  if (mode == 2) {
    if (actionEnCours && strcmp(fileActions[actionCouranteIndex].intention, "AVANCER") == 0) {
      if (detecter_obstacle(trig_fwd, echo_fwd)) {
        stopMoteurs();
        actionEnCours = false;
        totalActions = 0;
        actionCouranteIndex = 0;
        Serial.println("ALERTE_OBSTACLE");
        Serial.println("SEQUENCE_TERMINEE");
      }
    }

    if (actionEnCours) {
      if (millis() >= finActionMillis) {
        stopMoteurs();
        actionEnCours = false;
        actionCouranteIndex++;
        delay(100);
      }
    } 
    else {
      if (actionCouranteIndex < totalActions) {
        char* intention = fileActions[actionCouranteIndex].intention;
        int valeur = fileActions[actionCouranteIndex].valeur;

        Serial.print("Execution : "); Serial.println(intention);

        bool actionReconnue = true;

        if (strcmp(intention, "AVANCER") == 0) {
          avancer();
          finActionMillis = millis() + ((unsigned long)valeur * 1720); 
        }
        else if (strcmp(intention,"RECULER") == 0){
          reculer();
          finActionMillis = millis() + ((unsigned long)valeur * 1720);
        }
        else if (strcmp(intention, "TOURNER_GAUCHE") == 0) {
          gauche();
          finActionMillis = millis() + ((unsigned long)valeur * 10);
        }
        else if (strcmp(intention, "TOURNER_DROITE") == 0 || strcmp(intention, "TOURNER") == 0) {
          droite();
          finActionMillis = millis() + ((unsigned long)valeur * 10);
        }
        else if (strcmp(intention, "STOP") == 0) {
          stopMoteurs();
          finActionMillis = millis() + ((unsigned long)valeur * 1000);
        }
        else {
          actionReconnue = false;
        }

        if (actionReconnue) {
          actionEnCours = true;
        } else {
          actionCouranteIndex++;
        }
      } 
      else if (totalActions > 0 && actionCouranteIndex == totalActions) {
        Serial.println("SEQUENCE_TERMINEE");
        totalActions = 0;
      }
    }
  }

  envoyerTelemetrie();
}
