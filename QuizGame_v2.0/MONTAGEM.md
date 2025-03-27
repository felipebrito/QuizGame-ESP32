# Guia de Montagem - Quiz Game v2.0.1

Este documento detalha como montar o hardware necessário para o sistema Quiz Game v2.0.1, que consiste em um ESP32 Master conectado ao computador via USB e três ESPs Cliente (um para cada jogador).

> **Nota**: Esta versão (2.0.1) foi atualizada para compatibilidade com ESP-IDF v5.3 e Arduino ESP32 Core v3.0+. Certifique-se de que está utilizando a versão correta do ESP32 Arduino Core ao compilar o código.

## Componentes Necessários

### Para o ESP32 Master:
- 1x ESP32 DevKit (recomendado: ESP32-WROOM-32)
- 1x cabo USB para conexão com o computador

### Para cada ESP32 Cliente (x3):
- 1x ESP32 DevKit (recomendado: ESP32-WROOM-32)
- 3x botões tipo arcade ou push button
- 3x resistores de 10k ohm (opcional, para pull-up externo)
- Fios de conexão
- Caixa protetora (opcional)
- Fonte de alimentação (bateria de lítio ou fonte USB portátil)

### Ferramentas:
- Soldador e solda
- Alicate de corte
- Ferro de estanho
- Multímetro (opcional, para teste)

## Diagrama de Conexão

### ESP32 Master:
- Apenas conectar ao computador via USB (sem componentes adicionais).

### ESP32 Cliente - Jogador 1:
```
ESP32 GPIO18 ──── Botão A ──── GND
ESP32 GPIO4  ──── Botão B ──── GND
ESP32 GPIO5  ──── Botão C ──── GND
ESP32 3.3V   ──── VCC dos botões (se necessário)
```

### ESP32 Cliente - Jogador 2:
```
ESP32 GPIO19 ──── Botão A ──── GND
ESP32 GPIO21 ──── Botão B ──── GND
ESP32 GPIO22 ──── Botão C ──── GND
ESP32 3.3V   ──── VCC dos botões (se necessário)
```

### ESP32 Cliente - Jogador 3:
```
ESP32 GPIO12 ──── Botão A ──── GND
ESP32 GPIO13 ──── Botão B ──── GND
ESP32 GPIO14 ──── Botão C ──── GND
ESP32 3.3V   ──── VCC dos botões (se necessário)
```

## Montagem Passo a Passo

### Para cada ESP32 Cliente:

1. **Preparação dos Botões:**
   - Se estiver usando botões arcade:
     - Conecte um fio ao terminal comum (COM) do botão.
     - Conecte outro fio ao terminal normalmente aberto (NO) do botão.
   - Se estiver usando push buttons simples:
     - Conecte um fio a cada terminal do botão.

2. **Conexão dos Botões:**
   - Conecte um terminal de cada botão ao pino GPIO correspondente no ESP32.
   - Conecte o outro terminal de cada botão ao GND.
   
   **Nota:** O ESP32 tem resistores pull-up internos, que são ativados no código (`INPUT_PULLUP`). Se preferir usar resistores pull-up externos, conecte-os entre o pino GPIO e o VCC (3.3V).

3. **Alimentação:**
   - Para testes iniciais, utilize o cabo USB.
   - Para a versão final, pode-se usar baterias de lítio ou fontes USB portáteis.
   - **Importante:** Se usar bateria, certifique-se de incluir um interruptor para ligar/desligar.

4. **Montagem na Caixa (Opcional):**
   - Faça furos na caixa para os botões.
   - Fixe os botões na caixa.
   - Monte o ESP32 dentro da caixa, fixando-o com parafusos ou fita dupla-face.
   - Faça um orifício para o cabo USB ou interruptor da bateria.

## Teste de Montagem

Após a montagem física, siga estes passos para testar:

1. Certifique-se de ter o Arduino IDE configurado com a versão correta do ESP32 Core (v3.0+ para ESP-IDF v5.3).
2. Carregue o código correspondente em cada ESP32 (Master e Clientes).
3. Conecte o ESP32 Master ao computador via USB.
4. Alimente os ESPs Cliente (via USB ou bateria).
5. Abra o Monitor Serial do Arduino IDE para o ESP32 Master.
6. Pressione os botões de cada ESP Cliente e verifique se o ESP32 Master está recebendo e exibindo as mensagens correspondentes.

## Dicas para Solução de Problemas

- **Erros de compilação relacionados ao ESP-NOW:**
  - Verifique se está usando o Arduino IDE com ESP32 Core v3.0+ para compatibilidade com ESP-IDF v5.3.
  - Se estiver usando uma versão anterior, você precisará modificar o código para usar a API antiga do ESP-NOW.

- **Botões não respondem:**
  - Verifique as conexões dos fios.
  - Confirme se está usando os pinos GPIO corretos.
  - Teste os botões com um multímetro (modo continuidade).

- **ESP Cliente não se comunica com o Master:**
  - Verifique se o endereço MAC do Master está corretamente definido no código do Cliente.
  - Certifique-se de que ambos os dispositivos estão ligados.
  - Verifique se a distância entre os dispositivos não é excessiva (ideal: até 10 metros com linha de visão).

- **Mensagens inconsistentes:**
  - Pode haver interferência eletromagnética - tente afastar os dispositivos de fontes de interferência.
  - Verifique se não há curto-circuito nas conexões.
  - Recarregue o código nos dispositivos afetados.

## Notas Finais

- Este sistema é projetado para funcionar em distâncias curtas (até 40 metros em campo aberto, menos em ambientes fechados).
- Para aumentar o alcance, considere usar antenas externas nas ESPs ou posicionar o Master em um local central.
- A vida útil da bateria dependerá do tipo utilizado e da frequência de uso. Baterias de lítio 18650 oferecem boa durabilidade.
- A versão 2.0.1 do software foi atualizada para compatibilidade com as versões mais recentes do ESP-IDF, o que pode impactar a compatibilidade com versões antigas do Arduino IDE. 