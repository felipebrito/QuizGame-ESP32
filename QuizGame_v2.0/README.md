# Quiz Game ESP32 v2.0 - Sistema com ESP-NOW

**Versão: 2.0.1**  
**Data: 28 de Março de 2025**

## Visão Geral

Esta é a versão 2.0.1 do sistema Quiz Game, que implementa um jogo de perguntas e respostas com 3 jogadores, cada um com 3 botões de resposta (A, B, C). A principal diferença em relação à versão 1.0 é a arquitetura de comunicação:

- Agora utiliza o protocolo **ESP-NOW** para comunicação sem fio entre dispositivos ESP32
- Elimina a dependência de um roteador WiFi
- Fornece maior estabilidade e alcance
- Usa comunicação Serial com o computador via uma ESP32 Master

## Arquitetura do Sistema

O sistema é composto por:

1. **ESP32 Master** - Conectada ao computador via USB, atua como hub central
2. **ESP32 Clientes** (3 unidades) - Uma para cada jogador, com 3 botões cada
3. **Software Chataigne** - Recebe dados via Serial e exibe estado dos botões

```
                                +-------------+
                                |             |
                                |  Chataigne  |
                                |             |
                                +------^------+
                                       |
                                       | Serial (USB)
                                       |
                                +------v------+
                                |             |
                                | ESP32 Master|
                                |             |
                                +------^------+
                                       |
                                       | ESP-NOW (Sem Fio)
                       +-----------+---+-----------+
                       |           |               |
                 +-----v-----++-----v-----++------v------+
                 | Cliente 1 || Cliente 2 || Cliente 3   |
                 | Jogador 1 || Jogador 2 || Jogador 3   |
                 | Botões A,B,C|| Botões A,B,C|| Botões A,B,C|
                 +-----------++-----------++-------------+
```

## Componentes do Hardware

- **4 × ESP32 Dev Module**:
  - 1 × ESP32 Master (conectada ao PC via USB)
  - 3 × ESP32 Clientes (uma para cada jogador)

- **9 × Botões de pressão** distribuídos entre as ESP32 Clientes:
  - **Cliente 1 (Jogador 1)**: 
    - Botão A: GPIO18
    - Botão B: GPIO4
    - Botão C: GPIO5
  - **Cliente 2 (Jogador 2)**: 
    - Botão A: GPIO19
    - Botão B: GPIO21
    - Botão C: GPIO22
  - **Cliente 3 (Jogador 3)**: 
    - Botão A: GPIO12
    - Botão B: GPIO13
    - Botão C: GPIO14

- **Alimentação**: 
  - Master: USB (do computador)
  - Clientes: USB ou baterias (opção para maior mobilidade)

## Arquivos do Projeto

1. **ESP32_Master.ino** - Código para a ESP32 Master que recebe dados ESP-NOW e envia via Serial
2. **ESP32_Cliente_Jogador1.ino** - Código para a ESP32 Cliente do Jogador 1
3. **ESP32_Cliente_Jogador2.ino** - Código para a ESP32 Cliente do Jogador 2 (idêntico ao Jogador 1, com ID alterado)
4. **ESP32_Cliente_Jogador3.ino** - Código para a ESP32 Cliente do Jogador 3 (idêntico ao Jogador 1, com ID alterado)
5. **ConfigurarChataigne_Serial.txt** - Guia de configuração do Chataigne para recepção Serial
6. **ObterEnderecoMAC.ino** - Script auxiliar para identificar os endereços MAC dos dispositivos

## Vantagens do ESP-NOW

1. **Independência de infraestrutura** - Não requer roteador WiFi ou rede existente
2. **Baixa latência** - Comunicação direta entre dispositivos (1-2ms)
3. **Maior alcance** - Até 50 metros em ambientes abertos
4. **Menor consumo de energia** - Ideal para operação por bateria
5. **Maior estabilidade** - Menos suscetível a interferências de rede

## Instalação

### Requisitos

- Arduino IDE 1.8.19+ ou Arduino IDE 2.x
- Biblioteca ArduinoJson by Benoit Blanchon
- ESP32 Board Support Package v2.0.5+ (para Arduino IDE 1.8.x) ou v3.0+ (para Arduino IDE 2.x)

### Configuração do Arduino IDE

#### Para Arduino IDE 1.8.x:

1. Adicione a URL do ESP32 no gerenciador de placas:
   - `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`

2. Instale as bibliotecas necessárias via Gerenciador de Bibliotecas:
   - ArduinoJson by Benoit Blanchon

3. Selecione a placa "ESP32 Dev Module" nas configurações

#### Para Arduino IDE 2.x (recomendado para ESP-IDF v5.3+):

1. Vá para Arquivo > Preferências
2. Na seção "URLs Adicionais para Gerenciadores de Placas", adicione:
   - `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`

3. Vá para Ferramentas > Placa > Gerenciador de Placas
4. Procure por ESP32 e instale a versão 3.0 ou superior
5. Após a instalação, selecione a placa "ESP32 Dev Module"

6. Instale as bibliotecas necessárias via Ferramentas > Gerenciar Bibliotecas:
   - ArduinoJson by Benoit Blanchon (versão 6.x ou superior)

### Versões de ESP-IDF Suportadas

Esta versão do código foi atualizada para funcionar com ESP-IDF v5.3+, que inclui mudanças na API do ESP-NOW. Especificamente:

- A assinatura do callback de recepção foi alterada
- Agora utiliza a estrutura `esp_now_recv_info_t` para informações do pacote recebido

### Obtenção e Configuração dos Endereços MAC

Para a comunicação ESP-NOW, cada dispositivo precisa conhecer o endereço MAC do dispositivo com o qual irá se comunicar. Siga estas etapas:

1. **Use o script utilitário fornecido**:
   - Carregue o arquivo **ObterEnderecoMAC.ino** em cada ESP32 (Master e Clientes)
   - Abra o Monitor Serial (115200 baud) para ver o endereço MAC
   - O script fornecerá o endereço no formato adequado para uso no código

2. **Para configurar o Master**:
   - Obtenha o endereço MAC de cada ESP32 Cliente usando o utilitário
   - Atualize os arrays `clienteMAC1`, `clienteMAC2`, e `clienteMAC3` no arquivo ESP32_Master.ino
   - Exemplo:
     ```cpp
     uint8_t clienteMAC1[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF}; // ESP32 Cliente 1
     uint8_t clienteMAC2[] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66}; // ESP32 Cliente 2
     uint8_t clienteMAC3[] = {0xAA, 0xBB, 0xCC, 0x11, 0x22, 0x33}; // ESP32 Cliente 3
     ```

3. **Para configurar cada Cliente**:
   - Obtenha o endereço MAC da ESP32 Master usando o utilitário
   - Atualize o array `masterMAC` em cada arquivo ESP32_Cliente_JogadorX.ino
   - Exemplo:
     ```cpp
     uint8_t masterMAC[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB}; // ESP32 Master
     ```

4. **Dica para identificação dos dispositivos**:
   - O utilitário também gera um ID único para cada ESP32 baseado no endereço MAC
   - Use este ID para identificar cada dispositivo físico e evitar confusão
   - Pode ser útil etiquetar cada ESP32 com seu ID e função (Master, Jogador 1, etc.)

### Ordem de Upload

1. Carregue primeiro o código ESP32_Master.ino na ESP32 que será conectada ao computador
2. Carregue o código ESP32_Cliente_Jogador1.ino na ESP32 do jogador 1
3. Repita para os demais jogadores, usando os códigos correspondentes

### Configuração do Chataigne

Siga as instruções detalhadas no arquivo **ConfigurarChataigne_Serial.txt**.

### Configurações Importantes

Para uma correta recepção das mensagens no Chataigne:

1. Em **Parameters > Message Structure**, selecione **Colon (:) separated**
2. Marque a opção **First value is the name**
3. Certifique-se que **Auto Add** esteja ativado
4. Selecione a **Port** correta com o dispositivo ESP32 Master conectado
5. Configure **Baud Rate** para **115200**
6. Verifique que **Is Connected** esteja ativado

Essas configurações garantem que os valores dos botões apareçam como componentes numéricos únicos que alternam entre 0 e 1, semelhantes ao campo "entry".

## Formato das Mensagens

### Mensagem de Botão
```json
{
  "tipo": "botao",
  "botao": "j1a",
  "estado": 1,
  "j1a": 1,
  "rssi": -65
}
```

### Mensagem de Status
```json
{
  "tipo": "status",
  "dispositivo": "Jogador 1",
  "online": true,
  "rssi": -65
}
```

## Comandos Disponíveis

- `status` - Solicita o estado atual de todos os dispositivos
- `ping 1` - Envia ping para o Jogador 1 (substituir número para outros jogadores)

## Solução de Problemas

1. **Erro de compilação relacionado à assinatura do callback ESP-NOW**:
   - Verifique a versão do ESP32 Arduino Core instalada (deve ser 3.0+ para ESP-IDF v5.3)
   - Para versões anteriores do core, pode ser necessário usar a versão anterior do código

2. **ESP32 Clientes não conectam**:
   - Verifique se os endereços MAC estão configurados corretamente
   - Use o script ObterEnderecoMAC.ino para confirmar os endereços MAC
   - Certifique-se de que os dispositivos estão próximos o suficiente
   - Reinicie todos os dispositivos

3. **Botões não respondem**:
   - Verifique as conexões físicas dos botões
   - Teste as ESP32 Clientes individualmente com o Serial Monitor
   - Confirme se as configurações de pinos estão corretas

4. **Chataigne não recebe dados**:
   - Verifique se a porta Serial correta está selecionada
   - Confirme se o baud rate está configurado como 115200
   - Teste a ESP32 Master com o Serial Monitor

## Diferenças em Relação à Versão 1.0

| Característica | Versão 1.0 | Versão 2.0/2.0.1 |
|----------------|------------|------------|
| Protocolo | WebSocket/WiFi | ESP-NOW |
| Dependência de infraestrutura | Roteador WiFi | Nenhuma |
| Número de dispositivos ESP32 | 1 | 4 |
| Conexão com PC | WiFi | Serial (USB) |
| Alcance | ~10-20m (depende do roteador) | ~30-50m (direto) |
| Latência | 20-100ms | 1-2ms |
| Confiabilidade | Média | Alta |
| Versão ESP-IDF suportada | Qualquer | v5.3+ (v2.0.1) |

## Notas de Versão

### Versão 2.0.1 (atual)
- Compatibilidade com ESP-IDF v5.3 e Arduino ESP32 Core 3.0+
- Atualização da API do ESP-NOW para corresponder às mudanças na biblioteca
- Correção de erros de compilação relacionados à assinatura dos callbacks
- Adição de utilitário para identificação de endereços MAC (ObterEnderecoMAC.ino)

### Versão 2.0
- Implementação do protocolo ESP-NOW para comunicação direta entre ESPs
- Arquitetura distribuída com ESP32 Master e Clientes
- Comunicação Serial com o Chataigne
- Detecção automática de conexão/desconexão
- Informações de RSSI para monitoramento de sinal

## Créditos e Licença

Este projeto é livre para uso não-comercial e modificação.

---

Documentação atualizada em 28/03/2025. 