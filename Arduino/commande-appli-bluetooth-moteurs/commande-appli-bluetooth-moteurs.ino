#include <AFMotor.h>

AF_DCMotor motor1(1); // ARR Gauche
AF_DCMotor motor2(2); // AV Gauche
AF_DCMotor motor3(3); // ARR Droit
AF_DCMotor motor4(4); // AV Droit

#define VMAX 230

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
}

void loop() {
  if (Serial3.available()) {
    char commande = Serial3.read();

    switch(commande){

      case 'W':
          stopMoteurs();
          break;
      case 'S':
          stopMoteurs();
          break;
      case 'F':
          avancer();
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

void reculer(){
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}

void gauche(){
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
}

void droite(){
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}