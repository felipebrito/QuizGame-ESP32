#include <esp_now.h>
#include <WiFi.h>
#include <ArduinoJson.h>

// Estrutura para receber os dados dos botões de cada cliente
typedef struct {
  int jogador;     // ID do jogador (1, 2, 3)
  char botao;      // Botão pressionado ('a', 'b', 'c')
  int estado;      // Estado do botão (1=pressionado, 0=solto)
  int rssi;        // Força do sinal do cliente
  int bateria;     // Nível de bateria (opcional, se alimentado por bateria)
} mensagem_botao_t;

// Buffer para mensagens
mensagem_botao_t dadosRecebidos;

// Buffer JSON para comunicação serial
StaticJsonDocument<512> jsonDoc;
char jsonBuffer[512];

// Estados atuais dos botões
int botaoJ1A = 0, botaoJ1B = 0, botaoJ1C = 0;
int botaoJ2A = 0, botaoJ2B = 0, botaoJ2C = 0;
int botaoJ3A = 0, botaoJ3B = 0, botaoJ3C = 0;

// Controle de tempo para envio periódico do estado
unsigned long ultimoEnvioEstado = 0;
const long intervaloEnvioEstado = 200; // Enviar a cada 200ms se houver botões pressionados

// Endereços MAC dos dispositivos clientes (preencher manualmente após verificar)
uint8_t clienteMAC1[] = {0xE4, 0x65, 0xB8, 0x79, 0x42, 0x6C}; // ESP32 Cliente 1 (Jogador 1)
uint8_t clienteMAC2[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Substituir com MAC real
uint8_t clienteMAC3[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; // Substituir com MAC real

// Estrutura para armazenar informações dos clientes
struct InfoCliente {
  uint8_t mac[6];
  String nome;
  bool online;
  unsigned long ultimoHeartbeat;
};

// Array de clientes
InfoCliente clientes[3];

// Controle de tempo para verificar status dos clientes
unsigned long ultimaVerificacao = 0;
const long intervaloVerificacao = 5000; // Verificar a cada 5 segundos

// Atualiza o estado de um botão e envia imediatamente
void atualizarEstadoBotao(int jogador, char botao, int novoEstado) {
  int* estadoAtual = NULL;
  String nomeVar;
  
  // Seleciona o ponteiro para o estado correto do botão
  if (jogador == 1) {
    if (botao == 'a') {
      estadoAtual = &botaoJ1A;
      nomeVar = "j1a";
    }
    else if (botao == 'b') {
      estadoAtual = &botaoJ1B;
      nomeVar = "j1b";
    }
    else if (botao == 'c') {
      estadoAtual = &botaoJ1C;
      nomeVar = "j1c";
    }
  } 
  else if (jogador == 2) {
    if (botao == 'a') {
      estadoAtual = &botaoJ2A;
      nomeVar = "j2a";
    }
    else if (botao == 'b') {
      estadoAtual = &botaoJ2B;
      nomeVar = "j2b";
    }
    else if (botao == 'c') {
      estadoAtual = &botaoJ2C;
      nomeVar = "j2c";
    }
  }
  else if (jogador == 3) {
    if (botao == 'a') {
      estadoAtual = &botaoJ3A;
      nomeVar = "j3a";
    }
    else if (botao == 'b') {
      estadoAtual = &botaoJ3B;
      nomeVar = "j3b";
    }
    else if (botao == 'c') {
      estadoAtual = &botaoJ3C;
      nomeVar = "j3c";
    }
  }
  
  // Se encontrou o botão e o valor mudou, atualiza e envia
  if (estadoAtual != NULL && *estadoAtual != novoEstado) {
    *estadoAtual = novoEstado;
    
    // Envia o valor no formato do entry
    Serial.print(nomeVar);
    Serial.println(novoEstado == 1 ? ":1" : ":0");
  }
}

// Função para enviar o estado de todos os botões
void enviarEstadosBotoes() {
  // Envia cada botão no formato do entry
  Serial.print("j1a"); Serial.println(botaoJ1A == 1 ? ":1" : ":0");
  Serial.print("j1b"); Serial.println(botaoJ1B == 1 ? ":1" : ":0");
  Serial.print("j1c"); Serial.println(botaoJ1C == 1 ? ":1" : ":0");
  Serial.print("j2a"); Serial.println(botaoJ2A == 1 ? ":1" : ":0");
  Serial.print("j2b"); Serial.println(botaoJ2B == 1 ? ":1" : ":0");
  Serial.print("j2c"); Serial.println(botaoJ2C == 1 ? ":1" : ":0");
  Serial.print("j3a"); Serial.println(botaoJ3A == 1 ? ":1" : ":0");
  Serial.print("j3b"); Serial.println(botaoJ3B == 1 ? ":1" : ":0");
  Serial.print("j3c"); Serial.println(botaoJ3C == 1 ? ":1" : ":0");
}

// Callback quando dados são recebidos - nova assinatura para ESP-IDF v5.3+
void OnDataRecv(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  // Obtem o endereço MAC de quem enviou
  const uint8_t *mac = info->src_addr;
  
  // Se recebemos dados de botão
  if (len == sizeof(mensagem_botao_t)) {
    memcpy(&dadosRecebidos, incomingData, sizeof(mensagem_botao_t));
    
    // Atualiza status do cliente correspondente
    for (int i = 0; i < 3; i++) {
      if (memcmp(mac, clientes[i].mac, 6) == 0) {
        clientes[i].online = true;
        clientes[i].ultimoHeartbeat = millis();
        
        // Se não for um heartbeat, atualiza o estado do botão
        if (dadosRecebidos.estado != -1) {
          atualizarEstadoBotao(dadosRecebidos.jogador, dadosRecebidos.botao, dadosRecebidos.estado);
        }
        break;
      }
    }
  }
}

void setup() {
  // Inicializa Serial
  Serial.begin(115200);
  delay(1000);
  
  // Envia rótulos do sistema
  Serial.println("ESP32");
  Serial.println("MASTER");
  Serial.println("ESP-NOW");
  Serial.println("Conecte");
  Serial.println("computador");
  Serial.println("via USB");
  Serial.println("EnderecoMAC");
  Serial.println("da");
  Serial.println("ESP Master:");
  Serial.println("00:00:00:00:00:00");
  Serial.println("inicializado");
  Serial.println("com");
  Serial.println("sucesso.");
  Serial.println("Aguardando");
  Serial.println("conexões");
  Serial.println("dos");
  Serial.println("clientes...");
  
  // Configura clientes conhecidos
  // Cliente 1 - Jogador 1
  memcpy(clientes[0].mac, clienteMAC1, 6);
  clientes[0].nome = "Jogador 1";
  clientes[0].online = false;
  clientes[0].ultimoHeartbeat = 0;
  
  // Cliente 2 - Jogador 2
  memcpy(clientes[1].mac, clienteMAC2, 6);
  clientes[1].nome = "Jogador 2";
  clientes[1].online = false;
  clientes[1].ultimoHeartbeat = 0;
  
  // Cliente 3 - Jogador 3
  memcpy(clientes[2].mac, clienteMAC3, 6);
  clientes[2].nome = "Jogador 3";
  clientes[2].online = false;
  clientes[2].ultimoHeartbeat = 0;
  
  // Inicializa ESP-NOW
  WiFi.mode(WIFI_STA);
  
  // Atualiza endereço MAC
  Serial.print("EnderecoMAC:"); 
  Serial.println(WiFi.macAddress());
  
  // Inicializa ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Erro inicializando ESP-NOW");
    return;
  }
  
  // Registra função de callback para receber dados
  esp_now_register_recv_cb(OnDataRecv);
  
  // Envia o estado inicial dos botões (todos soltos)
  enviarEstadosBotoes();
}

void loop() {
  // Verifica comandos recebidos via Serial
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    
    if (comando == "status") {
      enviarStatusGeral();
    }
    else if (comando.startsWith("ping ")) {
      // Extrai o número do jogador
      int jogador = comando.substring(5).toInt();
      if (jogador >= 1 && jogador <= 3) {
        enviarComandoCliente(jogador - 1, "ping");
      }
    }
  }
  
  // Verifica status dos clientes periodicamente
  unsigned long tempoAtual = millis();
  if (tempoAtual - ultimaVerificacao >= intervaloVerificacao) {
    ultimaVerificacao = tempoAtual;
    verificarStatusClientes();
  }
  
  // Verifica se há algum botão pressionado e envia atualizações periódicas
  if (tempoAtual - ultimoEnvioEstado >= intervaloEnvioEstado) {
    ultimoEnvioEstado = tempoAtual;
    
    // Verifica se algum botão está pressionado (estado > 0)
    if (botaoJ1A > 0 || botaoJ1B > 0 || botaoJ1C > 0 || 
        botaoJ2A > 0 || botaoJ2B > 0 || botaoJ2C > 0 || 
        botaoJ3A > 0 || botaoJ3B > 0 || botaoJ3C > 0) {
      // Envia estados dos botões pressionados novamente
      if (botaoJ1A > 0) { Serial.print("j1a"); Serial.println(":1"); }
      if (botaoJ1B > 0) { Serial.print("j1b"); Serial.println(":1"); }
      if (botaoJ1C > 0) { Serial.print("j1c"); Serial.println(":1"); }
      if (botaoJ2A > 0) { Serial.print("j2a"); Serial.println(":1"); }
      if (botaoJ2B > 0) { Serial.print("j2b"); Serial.println(":1"); }
      if (botaoJ2C > 0) { Serial.print("j2c"); Serial.println(":1"); }
      if (botaoJ3A > 0) { Serial.print("j3a"); Serial.println(":1"); }
      if (botaoJ3B > 0) { Serial.print("j3b"); Serial.println(":1"); }
      if (botaoJ3C > 0) { Serial.print("j3c"); Serial.println(":1"); }
    }
  }
}

// Envia um comando para um cliente específico
void enviarComandoCliente(int indiceCliente, String comando) {
  // Estrutura para o comando
  typedef struct {
    char comando[20];
  } comando_t;
  
  comando_t msg;
  strcpy(msg.comando, comando.c_str());
  
  // Envia o comando via ESP-NOW
  esp_err_t result = esp_now_send(clientes[indiceCliente].mac, (uint8_t *)&msg, sizeof(msg));
  
  if (result == ESP_OK) {
    Serial.print("Comando enviado com sucesso para ");
    Serial.println(clientes[indiceCliente].nome);
  } else {
    Serial.print("Erro ao enviar comando para ");
    Serial.println(clientes[indiceCliente].nome);
  }
}

// Verifica status de todos os clientes
void verificarStatusClientes() {
  unsigned long tempoAtual = millis();
  
  for (int i = 0; i < 3; i++) {
    // Se o cliente estava online e não recebemos heartbeat por 10 segundos
    if (clientes[i].online && (tempoAtual - clientes[i].ultimoHeartbeat > 10000)) {
      // Marca como offline
      clientes[i].online = false;
      
      // Envia status de cliente offline
      Serial.print("jogador");
      Serial.print(i+1);
      Serial.println("_online:0");
    }
  }
}

// Envia status geral de todos os clientes e estado atual dos botões
void enviarStatusGeral() {
  // Status de conectividade
  for (int i = 0; i < 3; i++) {
    Serial.print("jogador");
    Serial.print(i+1);
    Serial.print("_online:");
    Serial.println(clientes[i].online ? "1" : "0");
    
    if (clientes[i].online) {
      // Envia RSSI
      Serial.print("jogador");
      Serial.print(i+1);
      Serial.print("_rssi:");
      Serial.println(dadosRecebidos.rssi);
    }
  }
  
  // Agora envia estado atual de todos os botões
  enviarEstadosBotoes();
} 