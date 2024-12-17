#include "DHT.h"

// Definir pinos e o tipo do sensor DHT
#define DHTPIN 8        // Pino em que o DHT11 está conectado
#define DHTTYPE DHT11   // Define o tipo de sensor DHT

// Definir pinos dos relés
#define RELAY_LAMP 7    // Relé da lâmpada no pino 7
#define RELAY_COOLER 5  // Relé do cooler no pino 5
#define RELAY_PUMP 4    // Relé da bomba no pino 4

// Inicializar o sensor DHT
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);  // Iniciar comunicação serial
  dht.begin();         // Iniciar o sensor DHT
  
  // Definir os pinos dos relés como saída
  pinMode(RELAY_LAMP, OUTPUT);
  pinMode(RELAY_COOLER, OUTPUT);
  pinMode(RELAY_PUMP, OUTPUT);

  // Inicialmente desligar os relés
  digitalWrite(RELAY_LAMP, LOW);
  digitalWrite(RELAY_COOLER, LOW);
  digitalWrite(RELAY_PUMP, LOW);
}

void loop() {
  // Leitura dos sensores e controle dos atuadores
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int soilMoistureValue = analogRead(A5);
  int ldrValue = analogRead(A0);

  // Verificar se os dados de temperatura e umidade foram lidos corretamente
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Erro ao ler o sensor DHT!");
  } else {
    // Enviar dados pela serial
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.print(soilMoistureValue);
    Serial.print(",");
    Serial.print(ldrValue);

    // Ler status dos relés (atuadores)
    int lampStatus = digitalRead(RELAY_LAMP);
    int coolerStatus = digitalRead(RELAY_COOLER);
    int pumpStatus = digitalRead(RELAY_PUMP);

    Serial.print(",");
    Serial.print(lampStatus);
    Serial.print(",");
    Serial.print(coolerStatus);
    Serial.print(",");
    Serial.println(pumpStatus);
  }

  delay(2000);  // Aguarda 2 segundos para a próxima leitura
}