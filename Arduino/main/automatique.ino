#include "automatique.h"

void mode_auto(int trig_fwd, int echo_fwd, int trig_right, int echo_right) {
  obs_fwd = detecter_obstacle(trig_fwd, echo_fwd);
  obs_right = detecter_obstacle(trig_right, echo_right);

  switch(etat_present){
    case 0 :
      if (obs_fwd){
        stopMoteurs();
        etat_suivant = 3;
      }
      else avancer();
      break;

    case 3 :
      reculer();
      delay(300);
      gauche();
      delay(150);
      etat_suivant = 1;
      break;

    case 1 :
      if (obs_right){
        if (obs_fwd) etat_suivant = 3;
        else etat_suivant = 0;
      }
      else {
        etat_suivant = 0;
      }
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

  totalActions = 0;
  actionCouranteIndex = 0;
  actionEnCours = false;

  char* bloc = strtok(buffer, " ");

  while (bloc != NULL && totalActions < MAX_ACTIONS) {
    char* virgule = strchr(bloc, ',');
    
    if (virgule != NULL) {
      *virgule = '\0';
      char* intention = bloc;
      char* valeurStr = virgule + 1;

      strncpy(fileActions[totalActions].intention, intention, 19);
      fileActions[totalActions].valeur = atof(valeurStr);
      totalActions++;
    }
    bloc = strtok(NULL, " ");
  }
  
  Serial.print("Sequence enregistree. Actions : ");
  Serial.println(totalActions);
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
  set_speed(0);
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
  v_actuelle = speed;
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

  if (distance > 2 && distance < 50) return 1;
  else return 0;
}

void envoyerTelemetrie() {
  if (millis() - dernierEnvoiTelemetrie >= intervalleTelemetrie) {
    obs_fwd = detecter_obstacle(trig_fwd, echo_fwd);
    obs_right = detecter_obstacle(trig_right, echo_right);
    
    Serial.print("TELEMETRIE:");
    Serial.print(obs_fwd);
    Serial.print(",");
    Serial.print(obs_right);
    Serial.print(",");
    Serial.print(v_actuelle);
    Serial.print(",");
    Serial.println(mode);
    
    dernierEnvoiTelemetrie = millis();
  }
}
