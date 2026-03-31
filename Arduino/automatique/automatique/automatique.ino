#include <AFMotor.h>

AF_DCMotor motor1(1); // ARR Gauche
AF_DCMotor motor2(2); // AV Gauche
AF_DCMotor motor3(3); // ARR Droit
AF_DCMotor motor4(4); // AV Droit

const int trig_fwd = 30;
const int echo_fwd = 31;
const int trig_right = 40;
const int echo_right = 41;

#define VMAX 230

int etat_present = 0;
int etat_suivant = 1;

void setup() {
  Serial.begin(38400); 
  Serial3.begin(38400);
  
  motor1.setSpeed(VMAX); 
  motor2.setSpeed(VMAX);
  motor3.setSpeed(VMAX);
  motor4.setSpeed(VMAX); 

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
  switch(etat_present){
    case 0 :
      if (detecter_obstacle(trig_fwd,echo_fwd)){
        stopMoteurs();
        etat_suivant = 1;
      }
      else avancer();
      break;
    case 1 :
      if (detecter_obstacle(trig_right,echo_right)){
        stopMoteurs();
        etat_suivant = 0;
      }
      else gauche();
      break;
  }
}

void stopMoteurs(){
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);
}

void avancer(){
  motor1.run(FORWARD);      
  motor2.run(FORWARD);      
  motor3.run(FORWARD);      
  motor4.run(FORWARD);  
}

void gauche(){
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
}

int detecter_obstacle(int trig, int echo){
  digitalWrite(trig,LOW);
  delayMicroseconds(2);
  digitalWrite(trig,HIGH);
  delayMicroseconds(10);
  digitalWrite(trig,LOW);

  long duree = pulseIn(echo, HIGH, 30000);
  float distance = duree * 0.034/2;

  if (distance < 60) return 1;
  else return 0;
}
