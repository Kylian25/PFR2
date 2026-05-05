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

void mode_manuel(char bouton, int trig_fwd, int echo_fwd) {
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

void mode_requetes(String commande) {
  commande.trim();
  if (commande.length() == 0) return;

  char buffer[commande.length() + 1];
  commande.toCharArray(buffer, sizeof(buffer));

  char* bloc = strtok(buffer, " ");

  while (bloc != NULL) {
    char* intention = strtok(bloc, ",");
    char* valeurStr = strtok(NULL, ",");

    if (intention != NULL && valeurStr != NULL) {
      int valeur = atoi(valeurStr);
      Serial.print("Action recue : "); Serial.println(intention);

      if (strcmp(intention, "AVANCER") == 0) {
        avancer();
        finActionMillis = millis() + (valeur * 1720);
        actionEnCours = true;
        // ON NE MET PAS stopMoteurs() ICI
      } 
      else if (strcmp(intention, "TOURNER") == 0) {
        if (valeur > 0) droite(); else gauche();
        // Pour le virage, on peut garder un petit delay ou utiliser la même logique millis
        finActionMillis = millis() + 900; // Exemple 500ms pour tourner
        actionEnCours = true;
      }
      else if (strcmp(intention, "STOP") == 0) {
        stopMoteurs();
        actionEnCours = false;
      }
    }
    bloc = strtok(NULL, " ");
  }
  // SURTOUT : Supprime le stopMoteurs() qui était ici à la fin
  Serial.println("Sequence enregistree");
}

void avancer(){
  set_speed(V_DROIT);
  motor1.run(FORWARD);      
  motor2.run(FORWARD);      
  motor3.run(FORWARD);      
  motor4.run(FORWARD);

  if (dernierOrdre != 'F'){
    Serial.println('F');
    dernierOrdre = 'F';
  }
}

void reculer(){
  set_speed(V_DROIT);
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
    
  if (dernierOrdre != 'B') {
    Serial.println('B');
    dernierOrdre = 'B';
  }
}

void gauche(){
  set_speed(V_TURN);
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);

  if (dernierOrdre != 'L') {
    Serial.println('L');
    dernierOrdre = 'L';
  }
}

void droite(){
  set_speed(V_TURN);
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
    
  if (dernierOrdre != 'R') {
    Serial.println('R');
    dernierOrdre = 'R';
  }
}

void stopMoteurs(){
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);

  if (dernierOrdre != 'S') {
    Serial.println('S');
    dernierOrdre = 'S';
  }
}

void set_speed(int speed){
  motor1.setSpeed(speed); 
  motor2.setSpeed(speed);
  motor3.setSpeed(speed);
  motor4.setSpeed(speed);
  Serial.print("Vitesse à ");
  Serial.println(speed);
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

  if (distance > 2 && distance < 50){
    if (millis() - dernierEnvoi >= intervalle) {
        if (trig == 30) Serial.print("Obstacle devant à : ");
        else if (trig == 40) Serial.print("Obstacle à droite à : ");
        Serial.println(distance);
        dernierEnvoi = millis();
    }
    return 1;
  }
  else return 0;
}
