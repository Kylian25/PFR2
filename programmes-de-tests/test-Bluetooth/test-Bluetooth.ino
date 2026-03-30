#include <SoftwareSerial.h>


SoftwareSerial mySerial(0, 1);   // Rx & Tx
const int trig_fwd = 30;
const int echo_fwd = 31;
const int trig_right = 40;
const int echo_right = 41;

void setup() {
  Serial.begin(38400); 
  mySerial.begin(38400); 
  pinMode(trig_fwd,OUTPUT);
  pinMode(echo_fwd,INPUT);
  pinMode(trig_right,OUTPUT);
  pinMode(echo_right,INPUT);
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