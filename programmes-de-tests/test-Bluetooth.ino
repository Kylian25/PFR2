#include <SoftwareSerial.h>


SoftwareSerial mySerial(0, 1);   // Rx & Tx

void setup() {
  Serial.begin(38400); 
  mySerial.begin(38400); 
}

void loop() {
  if (mySerial.available()) {
    char commande = mySerial.read();
    Serial.println(commande);

    switch(commande){

      case 'W':
          stopMoteurs();
      case 'S':
          stopMoteurs();
      case 'F':
          avancer();
      case 'B':
          reculer();
      case 'L':
          gauche();
      case 'R':
          droite();
      default:
          stopMoteurs();
    }
  }
}


void stopMoteurs(){
  Serial.println("Moteurs à l'arrêt");
}

void avancer(){
  Serial.println("Avance");
}

void reculer(){
  Serial.println("reculer");
}

void gauche(){
  Serial.println("Gauche");
}

void droite(){
  Serial.println("Droite");
}