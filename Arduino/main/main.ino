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
int mode = 0;
unsigned long dernierEnvoi = 0;
const int intervalle = 500;

void setup() {
  Serial.begin(38400); 
  Serial3.begin(38400);
  
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
}

void loop() {
  if (Serial.available()) {
    char bouton = Serial.read();

    if (bouton == 'W') {
      mode = 1;
      Serial.println("Passage en mode automatique");
    }
    else if (bouton == 'w') {
      mode = 0;
      stopMoteurs();
      Serial.println("Passage en mode manuel");
    }
    
    if (mode == 0) {
      mode_manuel(bouton, trig_fwd, echo_fwd);
    }
  }

  if (mode == 1) {
    mode_auto(trig_fwd, echo_fwd, trig_right, echo_right);
  }
}
