# Guia de Montagem - Quiz Game ESP32

Este documento fornece instruções detalhadas para a montagem do hardware do projeto Quiz Game com ESP32.

## Lista de Materiais

- 1 × ESP32 Dev Module
- 9 × Botões de pressão (push buttons)
- 9 × Resistores de 10kΩ (opcional, pode usar pull-up interno)
- Fios de conexão
- Protoboard ou PCB para montagem
- Caixa para abrigar o circuito (opcional)
- Cabo USB para alimentação e programação
- Fonte de alimentação 5V (opcional, se não usar USB)

## Conexões dos Botões

### Jogador 1
- **Botão A**: Conecte um terminal ao GPIO18 e outro ao GND
- **Botão B**: Conecte um terminal ao GPIO4 e outro ao GND
- **Botão C**: Conecte um terminal ao GPIO5 e outro ao GND

### Jogador 2
- **Botão A**: Conecte um terminal ao GPIO19 e outro ao GND
- **Botão B**: Conecte um terminal ao GPIO21 e outro ao GND
- **Botão C**: Conecte um terminal ao GPIO22 e outro ao GND

### Jogador 3
- **Botão A**: Conecte um terminal ao GPIO12 e outro ao GND
- **Botão B**: Conecte um terminal ao GPIO13 e outro ao GND
- **Botão C**: Conecte um terminal ao GPIO14 e outro ao GND

## Diagrama de Conexão

```
ESP32                   Botões
┌────────┐              ┌─────┐
│        │              │     │
│ GPIO18 ├──────────────┤ J1A │
│        │              │     │
│ GPIO4  ├──────────────┤ J1B │
│        │              │     │
│ GPIO5  ├──────────────┤ J1C │
│        │              │     │
│ GPIO19 ├──────────────┤ J2A │
│        │              │     │
│ GPIO21 ├──────────────┤ J2B │
│        │              │     │
│ GPIO22 ├──────────────┤ J2C │
│        │              │     │
│ GPIO12 ├──────────────┤ J3A │
│        │              │     │
│ GPIO13 ├──────────────┤ J3B │
│        │              │     │
│ GPIO14 ├──────────────┤ J3C │
│        │              │     │
│ GND    ├────┬────┬────┤ GND │
└────────┘    │    │    └─────┘
              │    │
              │    └──── (Conecte todos os botões ao GND)
              └───────── (Comum para todos os botões)
```

## Passo a Passo da Montagem

1. **Preparação do ESP32**:
   - Conecte o ESP32 à protoboard
   - Conecte o pino GND do ESP32 à linha de terra da protoboard

2. **Configuração dos Botões**:
   - Para cada botão:
     - Coloque o botão na protoboard
     - Conecte um terminal ao pino GPIO correspondente
     - Conecte o outro terminal ao GND

3. **Resistores Pull-up (opcional)**:
   - Se não utilizar os resistores pull-up internos do ESP32:
     - Conecte um resistor de 10kΩ entre cada pino GPIO e VCC (3.3V)

4. **Teste de Continuidade**:
   - Use um multímetro para verificar se não há curtos-circuitos
   - Verifique se os botões fazem contato corretamente quando pressionados

5. **Montagem Final**:
   - Organize os fios para evitar curtos-circuitos
   - Se estiver usando uma caixa, posicione os botões de forma acessível para os jogadores
   - Identifique os botões de cada jogador (por exemplo, com cores ou etiquetas)

## Notas Importantes

- **Resistores Pull-up**: O código já configura os pinos para usar resistores pull-up internos do ESP32. Se preferir usar resistores externos, conecte-os entre os pinos GPIO e VCC (3.3V).

- **Alimentação**: O ESP32 pode ser alimentado via USB ou por uma fonte externa de 5V. Certifique-se de que a fonte tenha capacidade suficiente (pelo menos 500mA).

- **Layout Físico**: Posicione os botões de cada jogador de forma agrupada e intuitiva (idealmente em uma disposição triangular ou em linha).

- **Proteção**: Para uso prolongado, considere usar uma caixa de proteção e botões robustos.

## Testes Iniciais

Após a montagem, mas antes de fechar qualquer caixa ou fixar permanentemente:

1. Faça o upload do código "ESP32_TestePinos.ino" (se disponível) ou um código simples de teste para verificar se todos os botões estão funcionando corretamente

2. Pressione cada botão e verifique se o ESP32 detecta corretamente os pressionamentos

3. Somente após confirmar que todos os pinos estão funcionando, faça o upload do código final "ESP32_WebSocket.ino"

## Resolução de Problemas de Hardware

- **Botão não responde**: Verifique a conexão física e teste o pino com um código simples
- **Falsos positivos**: Pode ser necessário adicionar um capacitor de 0.1µF entre o pino e o GND para debounce
- **ESP32 reiniciando**: Verifique se a fonte de alimentação é adequada 