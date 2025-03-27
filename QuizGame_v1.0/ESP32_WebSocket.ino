#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// Configurações de WiFi
const char* ssid = "MikroTik-22074B";
const char* password = "";  // Password vazio conforme solicitado

// Configurações do WebSocket
const char* websocketHost = "192.168.88.253"; // IP do computador com Chataigne
const int websocketPort = 9999;              // Porta WebSocket no Chataigne
const char* websocketPath = "/";             // Caminho padrão

// Definição dos pinos dos botões
// Jogador 1 (respostas A B C)
const int BOTAO_1A = 18;  // GPIO18 (confirmado funcionando)
const int BOTAO_1B = 4;   // GPIO4 (confirmado funcionando)
const int BOTAO_1C = 5;   // GPIO5 (confirmado funcionando)

// Jogador 2 (respostas A B C)
const int BOTAO_2A = 19;  // GPIO19
const int BOTAO_2B = 21;  // GPIO21
const int BOTAO_2C = 22;  // GPIO22

// Jogador 3 (respostas A B C)
const int BOTAO_3A = 12;  // GPIO12
const int BOTAO_3B = 13;  // GPIO13
const int BOTAO_3C = 14;  // GPIO14

// Estado anterior dos botões
// Jogador 1
int estadoAnterior1A = HIGH;
int estadoAnterior1B = HIGH;
int estadoAnterior1C = HIGH;

// Jogador 2
int estadoAnterior2A = HIGH;
int estadoAnterior2B = HIGH;
int estadoAnterior2C = HIGH;

// Jogador 3
int estadoAnterior3A = HIGH;
int estadoAnterior3B = HIGH;
int estadoAnterior3C = HIGH;

// Objeto WebSocket
WebSocketsClient webSocket;

// Variáveis para controle de conexão e heartbeat
unsigned long ultimoHeartbeat = 0;
const long intervaloHeartbeat = 5000;  // Enviar heartbeat a cada 5 segundos
bool conectado = false;

// Buffer para mensagens JSON
StaticJsonDocument<256> jsonDoc;
char jsonBuffer[256];

void setup() {
  // Inicializa serial e pinos
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\nESP32 - Quiz Game - WebSocket - 3 Jogadores");
  Serial.println("Jogador 1: GPIO18, GPIO4, GPIO5");
  Serial.println("Jogador 2: GPIO19, GPIO21, GPIO22");
  Serial.println("Jogador 3: GPIO12, GPIO13, GPIO14");
  
  // Configuração dos pinos - Jogador 1
  pinMode(BOTAO_1A, INPUT_PULLUP);
  pinMode(BOTAO_1B, INPUT_PULLUP);
  pinMode(BOTAO_1C, INPUT_PULLUP);
  
  // Configuração dos pinos - Jogador 2
  pinMode(BOTAO_2A, INPUT_PULLUP);
  pinMode(BOTAO_2B, INPUT_PULLUP);
  pinMode(BOTAO_2C, INPUT_PULLUP);
  
  // Configuração dos pinos - Jogador 3
  pinMode(BOTAO_3A, INPUT_PULLUP);
  pinMode(BOTAO_3B, INPUT_PULLUP);
  pinMode(BOTAO_3C, INPUT_PULLUP);
  
  // Conectar ao WiFi
  WiFi.begin(ssid, password);
  
  Serial.print("Conectando ao WiFi ");
  int tentativas = 0;
  
  // Tenta conectar por 10 segundos
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
    yield();
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    
    // Configuração do WebSocket
    webSocket.begin(websocketHost, websocketPort, websocketPath);
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
    webSocket.enableHeartbeat(15000, 3000, 2);
    
    Serial.println("WebSocket iniciado!");
    Serial.print("Conectando ao servidor: ");
    Serial.print(websocketHost);
    Serial.print(":");
    Serial.println(websocketPort);
  } else {
    Serial.println("\nFalha na conexão WiFi");
    Serial.println("Continuando apenas com leitura de botões");
  }
}

void loop() {
  // Manter conexão WebSocket ativa
  if (WiFi.status() == WL_CONNECTED) {
    webSocket.loop();
  }
  
  // Envia heartbeat periódico
  if (conectado && millis() - ultimoHeartbeat > intervaloHeartbeat) {
    enviarStatusGeral();
    ultimoHeartbeat = millis();
  }

  // === JOGADOR 1 ===
  // Lê o estado atual dos botões do jogador 1
  int estadoAtual1A = digitalRead(BOTAO_1A);
  int estadoAtual1B = digitalRead(BOTAO_1B);
  int estadoAtual1C = digitalRead(BOTAO_1C);
  
  // Verifica mudanças no botão 1A (GPIO18)
  if (estadoAtual1A != estadoAnterior1A) {
    if (estadoAtual1A == LOW) {
      Serial.println("Jogador 1 - Botão A (GPIO18) pressionado");
      enviarEstadoBotao("j1a", 1);
    } else {
      Serial.println("Jogador 1 - Botão A (GPIO18) solto");
      enviarEstadoBotao("j1a", 0);
    }
    estadoAnterior1A = estadoAtual1A;
  }
  
  // Verifica mudanças no botão 1B (GPIO4)
  if (estadoAtual1B != estadoAnterior1B) {
    if (estadoAtual1B == LOW) {
      Serial.println("Jogador 1 - Botão B (GPIO4) pressionado");
      enviarEstadoBotao("j1b", 1);
    } else {
      Serial.println("Jogador 1 - Botão B (GPIO4) solto");
      enviarEstadoBotao("j1b", 0);
    }
    estadoAnterior1B = estadoAtual1B;
  }
  
  // Verifica mudanças no botão 1C (GPIO5)
  if (estadoAtual1C != estadoAnterior1C) {
    if (estadoAtual1C == LOW) {
      Serial.println("Jogador 1 - Botão C (GPIO5) pressionado");
      enviarEstadoBotao("j1c", 1);
    } else {
      Serial.println("Jogador 1 - Botão C (GPIO5) solto");
      enviarEstadoBotao("j1c", 0);
    }
    estadoAnterior1C = estadoAtual1C;
  }
  
  // === JOGADOR 2 ===
  // Lê o estado atual dos botões do jogador 2
  int estadoAtual2A = digitalRead(BOTAO_2A);
  int estadoAtual2B = digitalRead(BOTAO_2B);
  int estadoAtual2C = digitalRead(BOTAO_2C);
  
  // Verifica mudanças no botão 2A (GPIO19)
  if (estadoAtual2A != estadoAnterior2A) {
    if (estadoAtual2A == LOW) {
      Serial.println("Jogador 2 - Botão A (GPIO19) pressionado");
      enviarEstadoBotao("j2a", 1);
    } else {
      Serial.println("Jogador 2 - Botão A (GPIO19) solto");
      enviarEstadoBotao("j2a", 0);
    }
    estadoAnterior2A = estadoAtual2A;
  }
  
  // Verifica mudanças no botão 2B (GPIO21)
  if (estadoAtual2B != estadoAnterior2B) {
    if (estadoAtual2B == LOW) {
      Serial.println("Jogador 2 - Botão B (GPIO21) pressionado");
      enviarEstadoBotao("j2b", 1);
    } else {
      Serial.println("Jogador 2 - Botão B (GPIO21) solto");
      enviarEstadoBotao("j2b", 0);
    }
    estadoAnterior2B = estadoAtual2B;
  }
  
  // Verifica mudanças no botão 2C (GPIO22)
  if (estadoAtual2C != estadoAnterior2C) {
    if (estadoAtual2C == LOW) {
      Serial.println("Jogador 2 - Botão C (GPIO22) pressionado");
      enviarEstadoBotao("j2c", 1);
    } else {
      Serial.println("Jogador 2 - Botão C (GPIO22) solto");
      enviarEstadoBotao("j2c", 0);
    }
    estadoAnterior2C = estadoAtual2C;
  }
  
  // === JOGADOR 3 ===
  // Lê o estado atual dos botões do jogador 3
  int estadoAtual3A = digitalRead(BOTAO_3A);
  int estadoAtual3B = digitalRead(BOTAO_3B);
  int estadoAtual3C = digitalRead(BOTAO_3C);
  
  // Verifica mudanças no botão 3A (GPIO12)
  if (estadoAtual3A != estadoAnterior3A) {
    if (estadoAtual3A == LOW) {
      Serial.println("Jogador 3 - Botão A (GPIO12) pressionado");
      enviarEstadoBotao("j3a", 1);
    } else {
      Serial.println("Jogador 3 - Botão A (GPIO12) solto");
      enviarEstadoBotao("j3a", 0);
    }
    estadoAnterior3A = estadoAtual3A;
  }
  
  // Verifica mudanças no botão 3B (GPIO13)
  if (estadoAtual3B != estadoAnterior3B) {
    if (estadoAtual3B == LOW) {
      Serial.println("Jogador 3 - Botão B (GPIO13) pressionado");
      enviarEstadoBotao("j3b", 1);
    } else {
      Serial.println("Jogador 3 - Botão B (GPIO13) solto");
      enviarEstadoBotao("j3b", 0);
    }
    estadoAnterior3B = estadoAtual3B;
  }
  
  // Verifica mudanças no botão 3C (GPIO14)
  if (estadoAtual3C != estadoAnterior3C) {
    if (estadoAtual3C == LOW) {
      Serial.println("Jogador 3 - Botão C (GPIO14) pressionado");
      enviarEstadoBotao("j3c", 1);
    } else {
      Serial.println("Jogador 3 - Botão C (GPIO14) solto");
      enviarEstadoBotao("j3c", 0);
    }
    estadoAnterior3C = estadoAtual3C;
  }
  
  delay(10); // Pequeno delay para debounce
}

// Manipula eventos do WebSocket
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("WebSocket desconectado!");
      conectado = false;
      
      // Tentamos enviar uma notificação de desconexão, mas provavelmente não chegará
      // já que a conexão foi perdida
      break;
    
    case WStype_CONNECTED:
      Serial.print("WebSocket conectado a ");
      Serial.println((char *)payload);
      conectado = true;
      
      // Envia notificação de conexão
      enviarSinal("conectado");
      
      // Envia estado inicial após conectar
      delay(100);
      enviarStatusGeral();
      break;
    
    case WStype_TEXT:
      Serial.print("Recebido: ");
      Serial.println((char *)payload);
      
      // Analisa os comandos recebidos
      if (strcmp((char *)payload, "status") == 0) {
        enviarStatusGeral();
      } else if (strcmp((char *)payload, "vivo") == 0) {
        enviarSinal("sim_estou_vivo");
      } else if (strcmp((char *)payload, "ping") == 0) {
        enviarSinal("pong");
      } else if (strcmp((char *)payload, "reiniciar") == 0) {
        enviarSinal("reiniciando");
        ESP.restart();
      }
      break;
  }
}

// Envia o estado de um botão específico via WebSocket
void enviarEstadoBotao(const char* botao, int estado) {
  if (!conectado) return;
  
  jsonDoc.clear();
  
  // Formato mais simples e direto para o Chataigne
  jsonDoc["tipo"] = "botao";
  jsonDoc["botao"] = botao;
  jsonDoc["estado"] = estado;
  
  // Enviar o botão também no topo da estrutura para facilitar o mapeamento
  // Isso vai ajudar o Chataigne a mapear os valores diretamente
  jsonDoc[botao] = estado;
  
  serializeJson(jsonDoc, jsonBuffer);
  webSocket.sendTXT(jsonBuffer);
  
  Serial.print("Enviado: ");
  Serial.println(jsonBuffer);
  
  // Após enviar o estado de um botão, enviar atualização completa
  // para manter o estado global atualizado
  delay(10);
  enviarStatusGeral();
}

// Envia um sinal simples via WebSocket
void enviarSinal(const char* mensagem) {
  if (!conectado) return;
  
  jsonDoc.clear();
  jsonDoc["tipo"] = "sinal";
  jsonDoc["mensagem"] = mensagem;
  
  serializeJson(jsonDoc, jsonBuffer);
  webSocket.sendTXT(jsonBuffer);
  
  Serial.print("Enviado: ");
  Serial.println(jsonBuffer);
}

// Envia o estado geral do sistema
void enviarStatusGeral() {
  if (!conectado) return;
  
  // Limpa o documento JSON
  jsonDoc.clear();
  
  // Informações básicas do sistema
  jsonDoc["tipo"] = "status";
  jsonDoc["online"] = true;  // Sempre true quando enviado (indica que está online)
  jsonDoc["ip"] = WiFi.localIP().toString();
  jsonDoc["rssi"] = WiFi.RSSI();
  jsonDoc["uptime"] = millis() / 1000;
  
  // Estado dos botões do jogador 1 - colocados diretamente no objeto principal
  // para facilitar o mapeamento no Chataigne
  jsonDoc["j1a"] = digitalRead(BOTAO_1A) == LOW ? 1 : 0;
  jsonDoc["j1b"] = digitalRead(BOTAO_1B) == LOW ? 1 : 0;
  jsonDoc["j1c"] = digitalRead(BOTAO_1C) == LOW ? 1 : 0;
  
  // Estado dos botões do jogador 2
  jsonDoc["j2a"] = digitalRead(BOTAO_2A) == LOW ? 1 : 0;
  jsonDoc["j2b"] = digitalRead(BOTAO_2B) == LOW ? 1 : 0;
  jsonDoc["j2c"] = digitalRead(BOTAO_2C) == LOW ? 1 : 0;
  
  // Estado dos botões do jogador 3
  jsonDoc["j3a"] = digitalRead(BOTAO_3A) == LOW ? 1 : 0;
  jsonDoc["j3b"] = digitalRead(BOTAO_3B) == LOW ? 1 : 0;
  jsonDoc["j3c"] = digitalRead(BOTAO_3C) == LOW ? 1 : 0;
  
  // Adiciona objeto botoes para compatibilidade com a versão anterior
  JsonObject botoes = jsonDoc.createNestedObject("botoes");
  botoes["j1a"] = digitalRead(BOTAO_1A) == LOW ? 1 : 0;
  botoes["j1b"] = digitalRead(BOTAO_1B) == LOW ? 1 : 0;
  botoes["j1c"] = digitalRead(BOTAO_1C) == LOW ? 1 : 0;
  botoes["j2a"] = digitalRead(BOTAO_2A) == LOW ? 1 : 0;
  botoes["j2b"] = digitalRead(BOTAO_2B) == LOW ? 1 : 0;
  botoes["j2c"] = digitalRead(BOTAO_2C) == LOW ? 1 : 0;
  botoes["j3a"] = digitalRead(BOTAO_3A) == LOW ? 1 : 0;
  botoes["j3b"] = digitalRead(BOTAO_3B) == LOW ? 1 : 0;
  botoes["j3c"] = digitalRead(BOTAO_3C) == LOW ? 1 : 0;
  
  serializeJson(jsonDoc, jsonBuffer);
  webSocket.sendTXT(jsonBuffer);
  
  Serial.print("Status enviado: ");
  Serial.println(jsonBuffer);
} 