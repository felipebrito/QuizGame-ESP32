#include <esp_now.h>
#include <WiFi.h>

// Definição de constantes
#define JOGADOR_ID 2  // Este é o Jogador 2

// Definição dos pinos dos botões
const int BOTAO_A = 19; // GPIO19
const int BOTAO_B = 21; // GPIO21
const int BOTAO_C = 22; // GPIO22

// Estado anterior dos botões
int estadoAnteriorA = HIGH;
int estadoAnteriorB = HIGH;
int estadoAnteriorC = HIGH;

// Endereço MAC da ESP32 Master (preencher manualmente após verificar)
uint8_t masterMAC[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Substituir com MAC real

// Estrutura para enviar informações dos botões
typedef struct {
  int jogador;     // ID do jogador (1, 2, 3)
  char botao;      // Botão pressionado ('a', 'b', 'c')
  int estado;      // Estado do botão (1=pressionado, 0=solto)
  int rssi;        // Força do sinal
  int bateria;     // Nível de bateria (simulado aqui, poderia ser real com monitoramento)
} mensagem_botao_t;

// Estrutura para receber comandos
typedef struct {
  char comando[20];
} comando_t;

// Variáveis de controle
bool pareado = false;
unsigned long ultimoHeartbeat = 0;
const long intervaloHeartbeat = 2000; // Heartbeat a cada 2 segundos

// Callback quando dados são enviados
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  if (status == ESP_NOW_SEND_SUCCESS) {
    // Envio com sucesso
  } else {
    // Falha no envio
    Serial.println("Erro ao enviar dados");
  }
}

// Callback quando dados são recebidos - nova assinatura para ESP-IDF v5.3+
void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  // Processa comandos recebidos do master
  if (len == sizeof(comando_t)) {
    comando_t comando;
    memcpy(&comando, incomingData, sizeof(comando_t));
    
    String comandoStr = String(comando.comando);
    
    if (comandoStr == "ping") {
      enviarHeartbeat();
      Serial.println("Ping recebido, enviando resposta");
    }
    else if (comandoStr == "reset") {
      ESP.restart();
    }
  }
}

void setup() {
  // Inicializa Serial (para debug)
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\nESP32 CLIENTE - Jogador " + String(JOGADOR_ID));
  Serial.println("Botões: GPIO19 (A), GPIO21 (B), GPIO22 (C)");
  
  // Configura pinos
  pinMode(BOTAO_A, INPUT_PULLUP);
  pinMode(BOTAO_B, INPUT_PULLUP);
  pinMode(BOTAO_C, INPUT_PULLUP);
  
  // Inicializa ESP-NOW
  WiFi.mode(WIFI_STA);
  
  // Imprime endereço MAC da ESP cliente
  Serial.print("Endereço MAC do Cliente: ");
  Serial.println(WiFi.macAddress());
  
  // Inicializa ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Erro inicializando ESP-NOW");
    return;
  }
  
  // Registra função de callback para enviar dados
  esp_now_register_send_cb(OnDataSent);
  
  // Registra função de callback para receber dados
  esp_now_register_recv_cb(OnDataRecv);
  
  // Registra o peer (ESP32 Master)
  esp_now_peer_info_t peerInfo;
  memcpy(peerInfo.peer_addr, masterMAC, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Adiciona peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Falha ao adicionar peer");
    return;
  }
  
  // Configuração concluída
  pareado = true;
  Serial.println("ESP-NOW configurado com sucesso");
  
  // Envia heartbeat inicial
  enviarHeartbeat();
}

void loop() {
  // Verifica o estado dos botões
  verificarBotoes();
  
  // Envia heartbeat periodicamente
  unsigned long tempoAtual = millis();
  if (tempoAtual - ultimoHeartbeat > intervaloHeartbeat) {
    enviarHeartbeat();
    ultimoHeartbeat = tempoAtual;
  }
  
  // Pequeno delay para estabilidade
  delay(10);
}

// Verifica o estado dos botões e envia se houve mudança
void verificarBotoes() {
  // Lê o estado atual dos botões
  int estadoAtualA = digitalRead(BOTAO_A);
  int estadoAtualB = digitalRead(BOTAO_B);
  int estadoAtualC = digitalRead(BOTAO_C);
  
  // Verifica botão A
  if (estadoAtualA != estadoAnteriorA) {
    if (estadoAtualA == LOW) {
      // Botão A pressionado
      Serial.println("Botão A pressionado");
      enviarEstadoBotao('a', 1);
    } else {
      // Botão A solto
      Serial.println("Botão A solto");
      enviarEstadoBotao('a', 0);
    }
    estadoAnteriorA = estadoAtualA;
  }
  
  // Verifica botão B
  if (estadoAtualB != estadoAnteriorB) {
    if (estadoAtualB == LOW) {
      // Botão B pressionado
      Serial.println("Botão B pressionado");
      enviarEstadoBotao('b', 1);
    } else {
      // Botão B solto
      Serial.println("Botão B solto");
      enviarEstadoBotao('b', 0);
    }
    estadoAnteriorB = estadoAtualB;
  }
  
  // Verifica botão C
  if (estadoAtualC != estadoAnteriorC) {
    if (estadoAtualC == LOW) {
      // Botão C pressionado
      Serial.println("Botão C pressionado");
      enviarEstadoBotao('c', 1);
    } else {
      // Botão C solto
      Serial.println("Botão C solto");
      enviarEstadoBotao('c', 0);
    }
    estadoAnteriorC = estadoAtualC;
  }
}

// Envia o estado de um botão específico
void enviarEstadoBotao(char botao, int estado) {
  if (!pareado) return;
  
  // Prepara os dados
  mensagem_botao_t msg;
  msg.jogador = JOGADOR_ID;
  msg.botao = botao;
  msg.estado = estado;
  msg.rssi = WiFi.RSSI();
  msg.bateria = 100; // Simulado (poderia ser real com monitoramento de bateria)
  
  // Envia os dados via ESP-NOW
  esp_err_t result = esp_now_send(masterMAC, (uint8_t *)&msg, sizeof(msg));
  
  if (result != ESP_OK) {
    Serial.println("Erro ao enviar dados");
  }
}

// Envia heartbeat para manter conexão ativa
void enviarHeartbeat() {
  if (!pareado) return;
  
  // Prepara os dados de heartbeat (usando a mesma estrutura com valores especiais)
  mensagem_botao_t msg;
  msg.jogador = JOGADOR_ID;
  msg.botao = 'h'; // 'h' para heartbeat
  msg.estado = -1; // -1 indica que não é um estado de botão, mas um heartbeat
  msg.rssi = WiFi.RSSI();
  msg.bateria = 100; // Simulado
  
  // Envia o heartbeat
  esp_now_send(masterMAC, (uint8_t *)&msg, sizeof(msg));
} 