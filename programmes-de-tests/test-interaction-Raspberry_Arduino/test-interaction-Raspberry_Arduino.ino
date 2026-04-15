void setup() {
  Serial.begin(38400); // La vitesse doit être la même sur les deux appareils
}

void loop() {
  if (Serial.available() > 0) {
    String commande = Serial.readStringUntil('\n'); // Lit le caractère envoyé par la Pi

    
    // Optionnel : Répondre à la Pi pour confirmer
    Serial.print("Commande recue : ");
    Serial.println(commande);
  }
}
