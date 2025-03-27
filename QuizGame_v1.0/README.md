# Quiz Game ESP32 - Sistema de Botões com WebSocket

**Versão: 1.0**  
**Data: 28 de Março de 2025**

## Visão Geral

Este projeto implementa um sistema de quiz game com 3 jogadores, cada um com 3 botões de resposta (A, B, C), utilizando um ESP32 para a comunicação via WebSocket com o software Chataigne. O sistema permite criar um jogo de perguntas e respostas com detecção imediata das respostas dos participantes.

## Componentes do Hardware

- **ESP32 Dev Module**
- **9 Botões de pressão** conectados aos seguintes pinos:
  - **Jogador 1**: 
    - Botão A: GPIO18
    - Botão B: GPIO4
    - Botão C: GPIO5
  - **Jogador 2**: 
    - Botão A: GPIO19
    - Botão B: GPIO21
    - Botão C: GPIO22
  - **Jogador 3**: 
    - Botão A: GPIO12
    - Botão B: GPIO13
    - Botão C: GPIO14
- **Resistores pull-up** (internos do ESP32, ativados no código)
- **Alimentação**: USB ou fonte 5V

## Arquivos do Projeto

1. **ESP32_WebSocket.ino** - Código principal para o ESP32 usando comunicação WebSocket
2. **ESP32_Simples.ino** - Versão alternativa usando comunicação UDP (backup)
3. **ConfigurarChataigne_WebSocket_Atualizado.txt** - Guia de configuração do Chataigne para WebSocket
4. **Solucao_Deteccao_Offline.txt** - Solução opcional para detectar quando o ESP32 está offline

## Funcionalidades

- Comunicação bidirecional via WebSocket
- Formato JSON para estruturação das mensagens
- Status completo do sistema (IP, RSSI, uptime)
- Estado em tempo real de todos os botões
- Comandos remotos (status, vivo, ping, reiniciar)
- Detecção automática de pressionamento dos botões
- Integração direta com Chataigne para visualização e controle

## Instalação

### Requisitos

- Arduino IDE 1.8.19 ou superior
- Bibliotecas:
  - WebSockets by Markus Sattler
  - ArduinoJson by Benoit Blanchon
- ESP32 Board Support Package

### Configuração do Arduino IDE

1. Adicione a URL do ESP32 no gerenciador de placas:
   - `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`

2. Instale as bibliotecas necessárias via Gerenciador de Bibliotecas:
   - WebSockets by Markus Sattler
   - ArduinoJson by Benoit Blanchon

3. Selecione a placa "ESP32 Dev Module" nas configurações

### Configuração do Chataigne

1. Instale o Chataigne (disponível em: https://benjamin.kuperberg.fr/chataigne/)
2. Crie um novo módulo WebSocket
3. Configure como Server na porta 9999
4. Ative a opção "Is Bound"
5. Configure "Message Structure" como JSON
6. Adicione valores para cada botão (j1a, j1b, j1c, j2a, j2b, j2c, j3a, j3b, j3c)

### Configuração Alternativa com UDP

Se precisar usar a versão UDP (ESP32_Simples.ino):

1. Crie um novo módulo UDP em vez de WebSocket
2. Configure a porta local para 9999
3. Em **Parameters > Message Structure**, selecione **Colon (:) separated**
4. Marque a opção **First value is the name**
5. Certifique-se que **Auto Add** esteja ativado
6. Verifique que **Is Bound** esteja ativado

As configurações de Message Structure garantem que os valores dos botões apareçam como componentes numéricos únicos que alternam entre 0 e 1, importante para a correta visualização no Chataigne.

## Formato das Mensagens

### Mensagem de Botão Pressionado
```json
{
  "tipo": "botao",
  "botao": "j1a",
  "estado": 1,
  "j1a": 1
}
```

### Mensagem de Status
```json
{
  "tipo": "status",
  "online": true,
  "ip": "192.168.88.xxx",
  "rssi": -65,
  "uptime": 120,
  "j1a": 0, "j1b": 0, "j1c": 0,
  "j2a": 0, "j2b": 0, "j2c": 0,
  "j3a": 0, "j3b": 0, "j3c": 0,
  "botoes": {
    "j1a": 0, "j1b": 0, "j1c": 0,
    "j2a": 0, "j2b": 0, "j2c": 0,
    "j3a": 0, "j3b": 0, "j3c": 0
  }
}
```

## Comandos Disponíveis

- `status` - Solicita o estado atual de todos os botões
- `vivo` - Verifica se o ESP32 está respondendo
- `ping` - Teste simples de conexão
- `reiniciar` - Reinicia o ESP32

## Solução de Problemas

1. **Conexão WebSocket falha**:
   - Verifique se o endereço IP e porta estão corretos
   - Certifique-se de que o ESP32 está na mesma rede que o computador rodando Chataigne
   - Verifique se não há firewall bloqueando a conexão

2. **Botões não respondem**:
   - Verifique as conexões físicas dos botões
   - Teste os pinos individualmente com um código simples
   - Verifique se os resistores pull-up estão funcionando

3. **Mensagens não aparecem no Chataigne**:
   - Verifique se o WebSocket está configurado como server e está bound
   - Confirme se o formato de mensagem está configurado como JSON
   - Reinicie o Chataigne e o ESP32

## Notas de Versão

### Versão 1.0 (atual)
- Implementação inicial com WebSocket
- Suporte para 3 jogadores com 3 botões cada
- Comunicação bidirecional estável
- Formato JSON para mensagens
- Integração completa com Chataigne

## Histórico de Desenvolvimento

O projeto evoluiu de uma comunicação UDP simples para WebSocket, garantindo maior confiabilidade e recursos. O sistema foi testado e validado em ambiente real, demonstrando estabilidade e baixa latência nas respostas.

## Licença

Este projeto é livre para uso não-comercial e modificação.

## Contato

Para suporte ou dúvidas, entre em contato com o desenvolvedor.

---

Documentação gerada em 28/03/2025. 