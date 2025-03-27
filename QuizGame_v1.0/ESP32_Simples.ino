#include <WiFi.h>
#include <WiFiUdp.h>

// Configurações de WiFi
const char* ssid = "MikroTik-22074B";
const char* password = "";  // Password vazio conforme solicitado
const int udpPort = 9999;
IPAddress broadcastIP(255, 255, 255, 255); // Endereço de broadcast
IPAddress specificIP(192, 168, 88, 253);   // IP do computador (ajuste se necessário)
IPAddress subnetBroadcast(192, 168, 88, 255); // Broadcast específico da sub-rede

// Definição dos pinos dos botões
// Jogador 1 (respostas A B C)
int BOTAO_1A = 18;  // GPIO18 (confirmado funcionando)
const int BOTAO_1B = 4;  // GPIO4 (confirmado funcionando)
const int BOTAO_1C = 5;  // GPIO5 (confirmado funcionando)

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

// Objeto UDP
WiFiUDP udp;

// Buffer de recepção UDP
char packetBuffer[255];

void setup() {
  // Inicializa serial e pinos
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\nESP32 - Quiz Game - Configuração Final com 3 Jogadores");
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
  
  // Configuração WiFi básica
  WiFi.mode(WIFI_STA);
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
    
    // Inicia UDP
    udp.begin(udpPort);
    Serial.print("UDP iniciado na porta ");
    Serial.println(udpPort);
    
    // Envia mensagens de teste em diferentes formatos e destinos
    enviarMensagemTeste();
  } else {
    Serial.println("\nFalha na conexão WiFi");
    Serial.println("Continuando apenas com leitura de botões");
  }
}

void enviarMensagemTeste() {
  // Método 1: Broadcast total (255.255.255.255)
  Serial.println("Enviando para broadcast total...");
  udp.beginPacket(broadcastIP, udpPort);
  udp.println("teste_broadcast_total");
  udp.endPacket();
  delay(100);
  
  // Método 2: Broadcast da sub-rede (192.168.88.255)
  Serial.println("Enviando para broadcast da sub-rede...");
  udp.beginPacket(subnetBroadcast, udpPort);
  udp.println("teste_broadcast_subnet");
  udp.endPacket();
  delay(100);
  
  // Método 3: IP específico (192.168.88.253)
  Serial.println("Enviando para IP específico...");
  udp.beginPacket(specificIP, udpPort);
  udp.println("teste_ip_especifico");
  udp.endPacket();
  delay(100);
  
  // Método 4: Envio múltiplo para todas as portas possíveis
  for (int porta = 9995; porta <= 10005; porta++) {
    Serial.print("Enviando para porta alternativa: ");
    Serial.println(porta);
    
    udp.beginPacket(broadcastIP, porta);
    String msg = "teste_porta_" + String(porta);
    udp.println(msg);
    udp.endPacket();
    delay(50);
  }
  
  Serial.println("Testes de envio UDP concluídos!");
}

void enviarUDP(const char* mensagem, bool useBroadcast) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  // Envia para múltiplos destinos para garantir recepção
  
  // 1. Broadcast total
  udp.beginPacket(broadcastIP, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // 2. Broadcast da sub-rede
  udp.beginPacket(subnetBroadcast, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // 3. IP específico
  udp.beginPacket(specificIP, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  Serial.print("Enviado UDP: ");
  Serial.println(mensagem);
}

void loop() {
  // Verifica se há pacotes UDP recebidos
  int packetSize = udp.parsePacket();
  if (packetSize) {
    // Lê o pacote
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; // Null-terminator
      
      // Guarda o endereço e porta de quem enviou a mensagem para responder diretamente
      IPAddress clientIP = udp.remoteIP();
      int clientPort = udp.remotePort();
      
      Serial.print("Recebido UDP de ");
      Serial.print(clientIP);
      Serial.print(":");
      Serial.print(clientPort);
      Serial.print(" -> ");
      Serial.println(packetBuffer);
      
      // Atualiza o endereço específico para o que está comunicando agora
      specificIP = clientIP;
      
      // Se recebeu 'ping', responde com 'pong'
      if (String(packetBuffer).indexOf("ping") >= 0) {
        // Responde diretamente para quem enviou
        enviarRespostaDireta("pong", clientIP, clientPort);
      }
      
      // Se recebeu 'vivo', responde com confirmação
      if (String(packetBuffer).indexOf("vivo") >= 0) {
        // Responde diretamente para quem enviou
        enviarRespostaDireta("sim_estou_vivo", clientIP, clientPort);
      }
      
      // Se recebeu 'test', envia uma sequência de testes
      if (String(packetBuffer).indexOf("test") >= 0) {
        Serial.println("Executando testes de UDP...");
        
        // Responde diretamente para quem enviou
        enviarRespostaDireta("iniciando_testes", clientIP, clientPort);
        
        // Tenta várias portas próximas
        for (int porta = clientPort-2; porta <= clientPort+2; porta++) {
          String msg = "teste_porta_" + String(porta);
          enviarRespostaDireta(msg.c_str(), clientIP, porta);
        }
      }
    }
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
      enviarEstadoBotao("j1a 1");
    } else {
      Serial.println("Jogador 1 - Botão A (GPIO18) solto");
      enviarEstadoBotao("j1a 0");
    }
    estadoAnterior1A = estadoAtual1A;
  }
  
  // Verifica mudanças no botão 1B (GPIO4)
  if (estadoAtual1B != estadoAnterior1B) {
    if (estadoAtual1B == LOW) {
      Serial.println("Jogador 1 - Botão B (GPIO4) pressionado");
      enviarEstadoBotao("j1b 1");
    } else {
      Serial.println("Jogador 1 - Botão B (GPIO4) solto");
      enviarEstadoBotao("j1b 0");
    }
    estadoAnterior1B = estadoAtual1B;
  }
  
  // Verifica mudanças no botão 1C (GPIO5)
  if (estadoAtual1C != estadoAnterior1C) {
    if (estadoAtual1C == LOW) {
      Serial.println("Jogador 1 - Botão C (GPIO5) pressionado");
      enviarEstadoBotao("j1c 1");
    } else {
      Serial.println("Jogador 1 - Botão C (GPIO5) solto");
      enviarEstadoBotao("j1c 0");
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
      enviarEstadoBotao("j2a 1");
    } else {
      Serial.println("Jogador 2 - Botão A (GPIO19) solto");
      enviarEstadoBotao("j2a 0");
    }
    estadoAnterior2A = estadoAtual2A;
  }
  
  // Verifica mudanças no botão 2B (GPIO21)
  if (estadoAtual2B != estadoAnterior2B) {
    if (estadoAtual2B == LOW) {
      Serial.println("Jogador 2 - Botão B (GPIO21) pressionado");
      enviarEstadoBotao("j2b 1");
    } else {
      Serial.println("Jogador 2 - Botão B (GPIO21) solto");
      enviarEstadoBotao("j2b 0");
    }
    estadoAnterior2B = estadoAtual2B;
  }
  
  // Verifica mudanças no botão 2C (GPIO22)
  if (estadoAtual2C != estadoAnterior2C) {
    if (estadoAtual2C == LOW) {
      Serial.println("Jogador 2 - Botão C (GPIO22) pressionado");
      enviarEstadoBotao("j2c 1");
    } else {
      Serial.println("Jogador 2 - Botão C (GPIO22) solto");
      enviarEstadoBotao("j2c 0");
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
      enviarEstadoBotao("j3a 1");
    } else {
      Serial.println("Jogador 3 - Botão A (GPIO12) solto");
      enviarEstadoBotao("j3a 0");
    }
    estadoAnterior3A = estadoAtual3A;
  }
  
  // Verifica mudanças no botão 3B (GPIO13)
  if (estadoAtual3B != estadoAnterior3B) {
    if (estadoAtual3B == LOW) {
      Serial.println("Jogador 3 - Botão B (GPIO13) pressionado");
      enviarEstadoBotao("j3b 1");
    } else {
      Serial.println("Jogador 3 - Botão B (GPIO13) solto");
      enviarEstadoBotao("j3b 0");
    }
    estadoAnterior3B = estadoAtual3B;
  }
  
  // Verifica mudanças no botão 3C (GPIO14)
  if (estadoAtual3C != estadoAnterior3C) {
    if (estadoAtual3C == LOW) {
      Serial.println("Jogador 3 - Botão C (GPIO14) pressionado");
      enviarEstadoBotao("j3c 1");
    } else {
      Serial.println("Jogador 3 - Botão C (GPIO14) solto");
      enviarEstadoBotao("j3c 0");
    }
    estadoAnterior3C = estadoAtual3C;
  }
  
  delay(10); // Pequeno delay para debounce
}

// Envia uma resposta diretamente para o cliente que enviou uma mensagem
void enviarRespostaDireta(const char* mensagem, IPAddress clientIP, int clientPort) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  // Primeiro envia diretamente para o cliente que solicitou
  udp.beginPacket(clientIP, clientPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Em seguida, usa o mesmo método que está funcionando para os botões
  // para garantir que a mensagem apareça no console UDP do Chataigne
  
  // Método 1: Broadcast total
  udp.beginPacket(broadcastIP, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 2: Broadcast da sub-rede
  udp.beginPacket(subnetBroadcast, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 3: IP específico (porta padrão)
  udp.beginPacket(specificIP, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 4: Porta 9999 (redundante, mas garantido)
  udp.beginPacket(specificIP, 9999);
  udp.println(mensagem);
  udp.endPacket();
  
  Serial.print("Resposta enviada para ");
  Serial.print(clientIP);
  Serial.print(":");
  Serial.print(clientPort);
  Serial.print(" -> ");
  Serial.println(mensagem);
}

// Envia o estado do botão usando todos os métodos disponíveis
void enviarEstadoBotao(const char* mensagem) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  // Método 1: Broadcast total
  udp.beginPacket(broadcastIP, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 2: Broadcast da sub-rede
  udp.beginPacket(subnetBroadcast, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 3: IP específico (atualizado dinamicamente pelo último cliente)
  udp.beginPacket(specificIP, udpPort);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 4: Porta 9999
  udp.beginPacket(specificIP, 9999);
  udp.println(mensagem);
  udp.endPacket();
  
  // Método 5: Porta 10001 (às vezes usada pelo Chataigne)
  udp.beginPacket(specificIP, 10001);
  udp.println(mensagem);
  udp.endPacket();
  
  Serial.print("Estado do botão enviado: ");
  Serial.println(mensagem);
} 