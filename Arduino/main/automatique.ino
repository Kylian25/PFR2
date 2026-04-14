#include "automatique.h"

void mode_auto(int trig_fwd, int echo_fwd, int trig_right, int echo_right) {
  switch(etat_present){
    case 0 :
      if (detecter_obstacle(trig_fwd,echo_fwd)){
        etat_suivant = 1;
      }
      else avancer();
      break;
    case 1 :
      if (detecter_obstacle(trig_right,echo_right)){
        if (detecter_obstacle(trig_fwd,echo_fwd)) etat_suivant = 2;
        else etat_suivant = 0;
      }
      else gauche();
      break;
    case 2 :
      gauche();
      etat_suivant = 1;
      break;
  }

  etat_present = etat_suivant;
}

void mode_manuel(char bouton, int trig_fwd, int echo_fwd){
    switch(bouton){
      case 'S':
          stopMoteurs();
          break;
      case 'F':
          if (detecter_obstacle(trig_fwd,echo_fwd)) stopMoteurs();
          else avancer();
          break;
      case 'B':
          reculer();
          break;
      case 'L':
          gauche();
          break;
      case 'R':
          droite();
          break;
    }
}

void avancer(){
  set_speed(V_DROIT);
  motor1.run(FORWARD);      
  motor2.run(FORWARD);      
  motor3.run(FORWARD);      
  motor4.run(FORWARD);  
}

void reculer(){
  set_speed(V_DROIT);
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}

void gauche(){
  set_speed(V_TURN);
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
}

void droite(){
  set_speed(V_TURN);
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}

void stopMoteurs(){
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);
}

void set_speed(int speed){
  motor1.setSpeed(speed); 
  motor2.setSpeed(speed);
  motor3.setSpeed(speed);
  motor4.setSpeed(speed);
}

int detecter_obstacle(int trig, int echo){
  digitalWrite(trig,LOW);
  delayMicroseconds(2);
  digitalWrite(trig,HIGH);
  delayMicroseconds(10);
  digitalWrite(trig,LOW);

  long duree = pulseIn(echo, HIGH, 30000);
  if (duree == 0) return 0;

  float distance = duree * 0.034/2;

  if (distance > 2 && distance < 50) return 1;
  else return 0;
}
