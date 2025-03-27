# Histórico de Mudanças - Quiz Game

## [v2.0.1] - 2024-03-28
### Alterado
- Atualização das funções de callback do ESP-NOW para compatibilidade com ESP-IDF v5.3
- Modificação da assinatura da função `OnDataRecv` em todos os códigos (Master e Clientes)
- Adaptação para usar a nova estrutura `esp_now_recv_info_t` para receber informações de pacotes

### Corrigido
- Erro de compilação relacionado à incompatibilidade da assinatura de callback do ESP-NOW em versões mais recentes do ESP-IDF
- Incompatibilidade na conversão de tipos entre a implementação antiga e a nova API

## [v2.0] - 2024-03-27
### Adicionado
- Implementação completa do protocolo ESP-NOW para comunicação direta entre ESPs
- Arquitetura Master-Cliente, com um ESP32 Master conectado ao computador via Serial
- Três ESPs Cliente para os jogadores (um por jogador)
- Suporte para três botões por jogador (A, B, C)
- Detecção automática de estado de conexão dos dispositivos
- Monitoramento de força do sinal (RSSI) para cada dispositivo
- Comunicação Serial com Chataigne para integração com o software de jogos
- Comandos remotos: ping, reset
- Heartbeat para manter a conexão ativa e monitorar dispositivos conectados

### Alterado
- Substituição do WebSocket por ESP-NOW para comunicação entre ESPs
- Substituição do WebSocket por Serial para comunicação com Chataigne
- Eliminação da dependência de infraestrutura WiFi (roteador)
- Melhoria na latência e confiabilidade do sistema
- Simplificação do processo de configuração (sem necessidade de credenciais WiFi)

### Corrigido
- Problemas de perda de conexão quando o roteador WiFi estava sobrecarregado
- Instabilidade na detecção do estado online/offline dos dispositivos
- Altas latências causadas pelo protocolo WebSocket

## [v1.0] - 2024-03-26
### Adicionado
- Implementação inicial do Quiz Game com ESP32
- Comunicação WebSocket para troca de dados
- Suporte para três jogadores com três botões cada
- Integração com Chataigne via WebSocket
- Interface para monitoramento do estado dos botões
- Sistema de detecção de botões pressionados

### Recursos
- Suporte para múltiplos jogadores
- Integração com software de controle Chataigne
- Comunicação sem fio via WiFi
- Detecção de pressionamento de botões em tempo real 