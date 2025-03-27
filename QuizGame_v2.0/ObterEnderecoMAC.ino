#include <WiFi.h>

void setup() {
  // Inicializa a comunicação serial
  Serial.begin(115200);
  delay(1000);
  
  // Inicializa o WiFi em modo estação para obter o MAC
  WiFi.mode(WIFI_STA);
  
  // Obtém o endereço MAC
  uint8_t mac[6];
  WiFi.macAddress(mac);
  
  // Exibe o endereço MAC no formato hexadecimal padronizado
  Serial.println("\n\n==================================");
  Serial.println("Utilitário para obter Endereço MAC");
  Serial.println("==================================");
  
  Serial.print("Endereço MAC: ");
  Serial.println(WiFi.macAddress());
  
  // Exibe o endereço MAC no formato para uso direto no código
  Serial.println("\nCopie a linha abaixo para o código:");
  Serial.print("uint8_t macAddress[] = {0x");
  Serial.print(mac[0], HEX);
  Serial.print(", 0x");
  Serial.print(mac[1], HEX);
  Serial.print(", 0x");
  Serial.print(mac[2], HEX);
  Serial.print(", 0x");
  Serial.print(mac[3], HEX);
  Serial.print(", 0x");
  Serial.print(mac[4], HEX);
  Serial.print(", 0x");
  Serial.print(mac[5], HEX);
  Serial.println("};");
  
  Serial.println("\nPara usar no Master, copie o endereço MAC de cada dispositivo:");
  Serial.println("- Execute este código em cada ESP32 Cliente");
  Serial.println("- Anote o endereço MAC exibido");
  Serial.println("- Substitua no ESP32_Master.ino nos arrays clienteMAC1, clienteMAC2 e clienteMAC3");
  
  Serial.println("\nPara usar nos Clientes:");
  Serial.println("- Execute este código na ESP32 Master");
  Serial.println("- Anote o endereço MAC exibido");
  Serial.println("- Substitua em cada ESP32_Cliente_JogadorX.ino no array masterMAC");
  
  // Cria uma identificação única para a placa baseada no MAC
  String deviceID = "ESP32_";
  deviceID += String(mac[4], HEX);
  deviceID += String(mac[5], HEX);
  
  Serial.print("\nID do dispositivo: ");
  Serial.println(deviceID);
  
  Serial.println("\n==================================");
  Serial.println("Mantenha este dispositivo conectado");
  Serial.println("Pressione qualquer tecla para repetir");
  Serial.println("==================================");
}

void loop() {
  // Se receber qualquer dado pela porta serial, repete as informações
  if (Serial.available()) {
    // Limpa o buffer
    while(Serial.available()) {
      Serial.read();
    }
    
    // Repete a informação do MAC
    uint8_t mac[6];
    WiFi.macAddress(mac);
    
    Serial.println("\n\n==================================");
    Serial.println("Endereço MAC:");
    Serial.println(WiFi.macAddress());
    
    Serial.print("\nFormato para código: ");
    Serial.print("uint8_t macAddress[] = {0x");
    Serial.print(mac[0], HEX);
    Serial.print(", 0x");
    Serial.print(mac[1], HEX);
    Serial.print(", 0x");
    Serial.print(mac[2], HEX);
    Serial.print(", 0x");
    Serial.print(mac[3], HEX);
    Serial.print(", 0x");
    Serial.print(mac[4], HEX);
    Serial.print(", 0x");
    Serial.print(mac[5], HEX);
    Serial.println("};");
    
    Serial.println("\n==================================");
    Serial.println("Pressione qualquer tecla para repetir");
    Serial.println("==================================");
  }
  
  delay(100);
} 