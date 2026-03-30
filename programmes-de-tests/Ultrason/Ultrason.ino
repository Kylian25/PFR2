const int trig = 40;
const int echo = 41;

void setup() {
  Serial.begin(9600);
  pinMode(trig,OUTPUT);
  pinMode(echo,INPUT);
  Serial.println("Test du capteur ultrason");
  
}

void loop() {
  digitalWrite(trig,LOW);
  delayMicroseconds(2);
  digitalWrite(trig,HIGH);
  delayMicroseconds(10);
  digitalWrite(trig,LOW);

  long duree = pulseIn(echo, HIGH, 30000);  // pulseIn attend que echo passe à HIGH
                                            // abandon si delai de repinse > 30ms

  // vitesse du son  = 340 m/s = 0.034 cm/microS
  float distance = duree * 0.034/2;      //  division par 2 = allé-retour
  Serial.println(duree);

  if (duree == 0){
    Serial.println("Aucun obstacle dans le champ");
  }
  else{
    Serial.println("Distance obstacle : ");
    Serial.println(distance);
    Serial.println(" cm");
  }
  delay(500);
}
