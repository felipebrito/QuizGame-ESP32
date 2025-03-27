# Changelog - Quiz Game ESP32

## Versão 1.0 (28/03/2025)

### Adicionado
- Implementação completa da comunicação WebSocket bidirecional
- Suporte para 3 jogadores com 3 botões cada (total de 9 botões)
- Envio de mensagens JSON estruturadas
- Resposta a comandos remotos (status, vivo, ping, reiniciar)
- Integração com o software Chataigne para visualização e controle
- Campo "online" para indicação de status de conexão
- Documentação completa do sistema

### Configurações
- Pinos dos botões:
  - Jogador 1: GPIO18, GPIO4, GPIO5
  - Jogador 2: GPIO19, GPIO21, GPIO22
  - Jogador 3: GPIO12, GPIO13, GPIO14
- Porta WebSocket: 9999
- Formato de mensagens: JSON

## Versão 0.2 (25/03/2025)

### Adicionado
- Comunicação UDP implementada
- Detecção de botões para o Jogador 1
- Testes de funcionamento com envio para múltiplas portas UDP
- Verificação de conexão com comando "vivo"

### Corrigido
- Problemas de comunicação unidirecional UDP
- Configuração de rede para ESP32

## Versão 0.1 (22/03/2025)

### Adicionado
- Configuração inicial do ESP32
- Testes de conexão WiFi
- Primeiros testes com botões
- Estrutura básica do código

### Investigado
- Diferentes opções de comunicação (UDP, WebSocket)
- Compatibilidade com o software Chataigne
- Pinos disponíveis no ESP32 para botões 