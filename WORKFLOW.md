# Workflow do Quiz Game

## Visão Geral do Sistema

O Sistema de Quiz Game é composto por quatro componentes principais:

1. **Hardware (ESP32)** - Controladores físicos para os jogadores
2. **API REST (Flask)** - Backend que gerencia a lógica do jogo
3. **Chataigne** - Software de middleware que orquestra a comunicação
4. **Resolume Arena** - Software de visualização para a audiência

## Fluxo Básico do Jogo

### 1. Inicialização do Sistema

1. Ligar os controladores ESP32 (versão WebSocket ou ESP-NOW)
2. Iniciar o servidor Flask para a API REST (`python app.py`)
3. Abrir o projeto Chataigne (`Quiz.noisette`)
4. Abrir o Resolume Arena com o template do jogo

### 2. Configuração da Partida

1. Em Chataigne, verificar as conexões com:
   - ESP32 (via Serial ou WebSocket)
   - API REST (HTTP Module)
   - Resolume (OSC Module)
2. Certificar-se de que todos os jogadores estão conectados (verificar no log do Chataigne)

### 3. Ciclo de Jogo Completo

#### Modo Apresentação (Idle)
1. Antes de iniciar um jogo, o sistema entra em modo apresentação
2. Exibe mensagem personalizada e tema escolhido
3. Serve como tela de espera entre jogos
4. Pode ser ativado a qualquer momento com `POST /api/modo_apresentacao`

#### Iniciar uma Nova Partida
1. Clicar no botão "Iniciar Jogo" em Chataigne
2. O sistema reseta as pontuações e configura o estado inicial
3. Estado muda para "iniciada"

#### Para Cada Rodada
1. Clicar no botão "Próxima Rodada" em Chataigne
2. O sistema:
   - Avança para a próxima pergunta
   - Reseta o timer automaticamente
   - Envia a pergunta e as opções para o Resolume
   - Estado muda para "rodada_ativa"
3. Clicar no botão "Iniciar Timer" (ou é iniciado automaticamente)
4. Os jogadores respondem usando os controladores ESP32
5. O sistema:
   - Registra a resposta e o tempo de cada jogador
   - Atualiza o tempo restante no Resolume
   - Notifica quando o tempo se esgota

#### Finalização da Rodada
1. Quando o timer acaba ou todas as respostas são recebidas:
   - O sistema calcula pontuações pela velocidade e precisão
   - Exibe feedback visual para respostas corretas/incorretas
   - Prepara-se para a próxima rodada

#### Finalização da Partida
1. Após a última rodada (quando rodada_atual > total_rodadas):
   - Sistema detecta automaticamente o fim da partida
   - Estado muda para "finalizado"
   - A classificação final é calculada
   - Endpoint `GET /api/verificar_fim_jogo` confirma o status
2. Exibir os resultados em Resolume:
   - Pontuações finais de todos os jogadores
   - Destaque para o vencedor
3. Anúncio do vencedor com efeitos visuais/sonoros

#### Reinício ou Nova Partida
1. Para reiniciar com os mesmos jogadores:
   - Usar endpoint `POST /api/reiniciar`
   - Pontuações são zeradas, jogadores mantidos
   - Estado volta para "aguardando"
2. Para voltar ao início:
   - Usar endpoint `POST /api/modo_apresentacao`
   - Sistema entra em modo idle com tela personalizada

## Estados do Jogo

- **aguardando**: O jogo ainda não foi iniciado
- **iniciada**: Jogo iniciado, mas nenhuma rodada em andamento
- **rodada_ativa**: Uma rodada está em andamento
- **finalizada**: O jogo foi concluído
- **apresentacao**: Modo idle/espera com tela personalizada

## Ciclo do Timer

1. O timer é resetado automaticamente ao iniciar uma nova rodada
2. Pode ser iniciado manualmente ou automaticamente (30 segundos por padrão)
3. O tempo restante é consultado a cada segundo e exibido
4. Quando o tempo acaba, notificações são enviadas

## Diagrama de Estados

```
                         ┌──────────────┐
                         │              │
                ┌────────►  apresentacao│
                │        │   (idle)     │
                │        └──────▲───────┘
  ┌──────────┐  │               │        
  │reiniciar │  │               │        
  │          │  │   ┌───────────┴───────┐
┌─┴──────────▼──┴───┤                   │
│                    │    aguardando    │
│    finalizada      │                  │
│   (fim de jogo)    │                  │
└───────▲────────────┴─────────┬────────┘
        │                      │
        │ última rodada        │ iniciar jogo
        │                      │
        │                      ▼
┌───────┴────────────┐  ┌─────────────────┐
│                    │  │                  │
│    rodada_ativa    ◄──┤     iniciada    │
│    (pergunta)      │  │                  │
└────────────────────┘  └──────────────────┘
```

## Comandos da API REST

- `GET /api/status` - Verificar estado atual do jogo
- `POST /api/iniciar` - Iniciar novo jogo
- `POST /api/proxima_rodada` - Avançar para próxima rodada
- `GET /api/pergunta_atual` - Obter pergunta da rodada
- `POST /api/enviar_resposta` - Enviar resposta de jogador
- `GET /api/resultados` - Obter classificação
- `POST /api/iniciar_timer` - Iniciar timer da rodada
- `GET /api/tempo_restante` - Verificar tempo restante
- `POST /api/cancelar_timer` - Cancelar timer da rodada
- `POST /api/reiniciar` - Reiniciar jogo com os mesmos jogadores
- `POST /api/modo_apresentacao` - Ativar modo de espera/idle
- `GET /api/verificar_fim_jogo` - Verificar se o jogo está finalizado
- `GET /api/temas` - Listar temas disponíveis de perguntas

## Troubleshooting Comum

### Problemas de Conexão
- Verificar se o servidor Flask está rodando (`python app.py`)
- Confirmar que as portas estão corretas (5001 para API)
- Verificar se o ESP32 está conectado corretamente

### Problemas de Jogo
- Se o timer não inicia, verificar logs do servidor
- Se as perguntas não aparecem, verificar conexão OSC com Resolume
- Se jogadores não conseguem responder, verificar conexão do ESP32

### Reiniciar o Sistema
1. Matar o processo do servidor Flask (`kill -9 $(pgrep -f "python app.py")`)
2. Reiniciar o servidor (`python app.py`)
3. Reconectar os módulos no Chataigne

## Fluxo de Dados

```
+---------------+    Serial/WebSocket    +----------------+
| Controladores |<-------------------->  |                |
|  ESP32        |                         |                |
+---------------+                         |                |
                                         |                |
+---------------+    HTTP (REST API)     |                |
| Servidor Flask|<-------------------->  |   Chataigne    |
|  (Backend)    |                         |                |
+---------------+                         |                |
                                         |                |
+---------------+    OSC Protocol        |                |
| Resolume Arena|<-------------------->  |                |
|  (Frontend)   |                         |                |
+---------------+                         +----------------+
```

## Integração com ESP32

### Versão 1.0 (WebSocket)
- Um único ESP32 conectado via WebSocket
- Formato de mensagens em JSON
- Conexão através da rede WiFi

### Versão 2.0 (ESP-NOW)
- Um ESP32 Master conectado via Serial
- Múltiplos ESP32 Clients para jogadores
- Comunicação direta, sem necessidade de WiFi

## Tratamento de Respostas

1. O jogador pressiona um botão (A, B ou C)
2. O ESP32 envia a resposta para o Chataigne
3. Chataigne envia a resposta para a API REST
4. A API verifica se a resposta está correta
5. A pontuação é calculada com base no tempo de resposta
6. O resultado é armazenado para a classificação final 