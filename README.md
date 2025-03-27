# Sistema de Quiz Game para ESP32 com versões WebSocket e ESP-NOW
# Quiz Game ESP32 - Sistema de Controle para Jogos de Perguntas e Respostas

**Data: 28 de Março de 2025**

Este repositório contém duas versões do sistema Quiz Game para ESP32, cada uma utilizando diferentes protocolos de comunicação:

## Versões Disponíveis

### [QuizGame_v1.0 (WebSocket)](./QuizGame_v1.0)

A versão 1.0 utiliza comunicação WebSocket e requer um roteador WiFi para conectar o ESP32 ao computador rodando o Chataigne.

**Características principais:**
- Protocolo WebSocket sobre WiFi
- Um único ESP32 para todos os jogadores
- Conexão via rede WiFi com o computador
- Formato JSON para mensagens
- Requer roteador WiFi como infraestrutura

### [QuizGame_v2.0 (ESP-NOW)](./QuizGame_v2.0)

A versão 2.0 utiliza o protocolo ESP-NOW para comunicação direta entre dispositivos ESP32, eliminando a necessidade de um roteador WiFi.

**Características principais:**
- Protocolo ESP-NOW para comunicação direta entre ESP32
- Um ESP32 Master conectado ao computador via USB/Serial
- Três ESP32 Clientes, um para cada jogador
- Formato de mensagens simples (nome:valor)
- Não requer infraestrutura WiFi externa

## Comparação entre as Versões

| Característica | Versão 1.0 (WebSocket) | Versão 2.0 (ESP-NOW) |
|----------------|------------------------|----------------------|
| Protocolo | WebSocket/WiFi | ESP-NOW |
| Dependência de infraestrutura | Roteador WiFi | Nenhuma |
| Número de dispositivos ESP32 | 1 | 4 |
| Conexão com PC | WiFi | Serial (USB) |
| Alcance | ~10-20m (depende do roteador) | ~30-50m (direto) |
| Latência | 20-100ms | 1-2ms |
| Confiabilidade | Média | Alta |
| Configuração no Chataigne | WebSocket Module | Serial Module |
| Formato de mensagem | JSON | Colon (:) separated |

## Requisitos Comuns

- Arduino IDE 1.8.19+ ou Arduino IDE 2.x
- ESP32 Board Support Package
- Bibliotecas adicionais (veja o README de cada versão)

## Notas importantes sobre a configuração do Chataigne

### Para a versão 1.0 (WebSocket/JSON)
- Em **Message Structure**, selecione **JSON**
- Desmarque a opção **First value is the name**

### Para a versão 2.0 (ESP-NOW/Serial)
- Em **Parameters > Message Structure**, selecione **Colon (:) separated**
- Marque a opção **First value is the name**
- Certifique-se que **Auto Add** esteja ativado

## Escolhendo uma Versão

- Use a **Versão 1.0 (WebSocket)** se:
  - Você já possui uma rede WiFi estável no local
  - Precisa usar apenas um ESP32
  - Prefere um formato de mensagem mais estruturado (JSON)
  - Não tem restrições severas de latência

- Use a **Versão 2.0 (ESP-NOW)** se:
  - Não tem acesso a um roteador WiFi ou a rede é instável
  - Precisa de maior alcance e conexão mais estável
  - Necessita de latência muito baixa
  - Pode utilizar múltiplos dispositivos ESP32

## Organização do Projeto

- **QuizGame_v1.0/** - Contém todos os arquivos da versão WebSocket
- **QuizGame_v2.0/** - Contém todos os arquivos da versão ESP-NOW
- **_INUTEIS/** - Contém versões anteriores e arquivos de teste (não necessários para uso)

## Licença

Este projeto é livre para uso não-comercial e modificação.

---

Documentação atualizada em 28/03/2025. 