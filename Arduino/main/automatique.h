#ifndef AUTOMATIQUE_H
#define AUTOMATIQUE_H

#include <AFMotor.h>

extern int etat_present;
extern int etat_suivant;
extern int mode;


void mode_auto(int trig_fwd, int echo_fwd, int trig_right, int echo_right);
void mode_manuel(char bouton, int trig_fwd, int echo_fwd);
void mode_requetes(String commande);
void avancer();
void reculer();
void gauche();
void droite();
void stopMoteurs();
void set_speed(int speed);
int detecter_obstacle(int trig, int echo);

#endif