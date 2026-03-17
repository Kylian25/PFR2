#include <AFMotor.h> 

// Définition des 4 moteurs
AF_DCMotor motor1(1); 
AF_DCMotor motor2(2); 
AF_DCMotor motor3(3); 
AF_DCMotor motor4(4);

void setup() {
  Serial.begin(9600);

  // Réglage de la vitesse pour tous (0 à 255)
  motor1.setSpeed(200); 
  motor2.setSpeed(200);
  motor3.setSpeed(200);
  motor4.setSpeed(200);
  
  // Initialisation à l'arrêt
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);
}

void loop() {
  Serial.println("Tous les moteurs en AVANT...");
  motor1.run(FORWARD);      
  motor2.run(FORWARD);      
  motor3.run(FORWARD);      
  motor4.run(FORWARD);      
  delay(2000);

  Serial.println("Arrêt...");
  motor1.run(RELEASE);      
  motor2.run(RELEASE);      
  motor3.run(RELEASE);      
  motor4.run(RELEASE);      
  delay(1000);

  Serial.println("Tous les moteurs en ARRIÈRE...");
  motor1.run(BACKWARD);     
  motor2.run(BACKWARD);     
  motor3.run(BACKWARD);     
  motor4.run(BACKWARD);     
  delay(2000);

  Serial.println("Arrêt...");
  motor1.run(RELEASE);      
  motor2.run(RELEASE);      
  motor3.run(RELEASE);      
  motor4.run(RELEASE);      
  delay(1000);
}