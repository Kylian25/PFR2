void setup() {
  Serial.begin(9600); // La vitesse doit être la même sur les deux appareils
}

void loop() {
  if (Serial.available() > 0) {
    char commande = Serial.read(); // Lit le caractère envoyé par la Pi

    
    // Optionnel : Répondre à la Pi pour confirmer
    Serial.print("Commande recue : ");
    Serial.println(commande);
  }
}
