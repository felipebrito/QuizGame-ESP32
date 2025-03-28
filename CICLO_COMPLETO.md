# Ciclo Completo do Quiz Game

Este documento detalha o ciclo completo do jogo, desde a inicialização até o encerramento, com foco especial nas transições entre estados e nos endpoints da API que controlam essas transições.

## Mapa de Estados

```
┌─────────────────┐       ┌───────────────┐       ┌──────────────┐
│  apresentacao   │───────►  aguardando   │───────►   iniciada   │
│  (modo idle)    │       │               │       │              │
└─────┬───────────┘       └───────────────┘       └──────┬───────┘
      │                           ▲                      │
      │                           │                      │
      │                           │                      │
      │                   ┌───────┴───────┐              │
      │                   │               │              │
      └───────────────────►  finalizada   ◄──────────────┘
                          │               │              ▲
                          └───────┬───────┘              │
                                  │                      │
                                  │                      │
                                  ▼                      │
                          ┌───────────────┐              │
                          │ rodada_ativa  │◄─────────────┘
                          │               │
                          └───────────────┘
```

## 1. Inicialização e Modo Apresentação

### Inicialização do Servidor
```
python app.py
```

### Modo Apresentação (idle)
- **Endpoint**: `POST /api/modo_apresentacao`
- **Descrição**: Configura o sistema para exibir uma tela de apresentação/espera.
- **Parâmetros**:
  - `mensagem`: Texto a ser exibido na tela (opcional)
  - `tema`: Tema visual a ser utilizado (opcional)
- **Comportamento**:
  - Reseta o estado do jogo para "apresentacao"
  - Zera a rodada atual
  - Desativa o timer
  - Prepara o sistema para o próximo jogo

### Exemplo de implementação de tela de apresentação
```python
# No backend (app.py)
@app.route('/api/modo_apresentacao', methods=['POST'])
def modo_apresentacao():
    dados = request.json if request.is_json else {}
    
    # Configura o estado de apresentação
    partida["status"] = "apresentacao"
    partida["rodada_atual"] = 0
    partida["timer_ativo"] = False
    
    # Opcionalmente recebe mensagem personalizada
    mensagem = dados.get("mensagem", "Quiz Game - Aguardando início da partida")
    tema = dados.get("tema", "default")
    
    return jsonify({
        "mensagem": "Modo apresentação ativado",
        "status": partida["status"],
        "tema": tema,
        "texto_apresentacao": mensagem
    })
```

## 2. Inicializar o Jogo

### Configuração inicial
- **Endpoint**: `POST /api/iniciar`
- **Descrição**: Inicia um novo jogo, zerando pontuações e configurando estado inicial.
- **Comportamento**:
  - Muda o estado para "iniciada"
  - Zera a rodada atual
  - Reseta as pontuações de todos os jogadores
  - Não carrega nenhuma pergunta ainda

### Verificação dos jogadores
- **Endpoint**: `GET /api/status`
- **Descrição**: Verifica o estado atual e os jogadores conectados.
- **Resposta**:
  ```json
  {
    "status": "iniciada",
    "rodada_atual": 0,
    "total_rodadas": 3,
    "participantes": [
      {"id": 1, "nome": "Jogador 1", "pontuacao": 0},
      {"id": 2, "nome": "Jogador 2", "pontuacao": 0},
      {"id": 3, "nome": "Jogador 3", "pontuacao": 0}
    ]
  }
  ```

## 3. Ciclo de Rodadas

### Avançar para uma rodada (1-N)
- **Endpoint**: `POST /api/proxima_rodada`
- **Descrição**: Avança para a próxima rodada, carregando a pergunta correspondente.
- **Comportamento**:
  - Incrementa o contador `rodada_atual`
  - Verifica se excedeu o total de rodadas:
    - Se sim, finaliza o jogo
    - Se não, ativa a rodada
  - Reseta o timer automaticamente
  - Estado muda para "rodada_ativa"

### Obter a pergunta atual
- **Endpoint**: `GET /api/pergunta_atual`
- **Descrição**: Obtém os dados da pergunta da rodada atual.
- **Resposta**:
  ```json
  {
    "id": 1,
    "texto": "Qual a capital do Brasil?",
    "tema": "Geografia",
    "respostas": [
      {"opcao": "A", "texto": "Rio de Janeiro"},
      {"opcao": "B", "texto": "São Paulo"},
      {"opcao": "C", "texto": "Brasília"}
    ],
    "status": "rodada_ativa",
    "rodada_atual": 1,
    "total_rodadas": 3
  }
  ```

### Iniciar o timer da rodada
- **Endpoint**: `POST /api/iniciar_timer`
- **Descrição**: Inicia a contagem regressiva para respostas.
- **Parâmetros**:
  - `duracao`: Duração em segundos (opcional, padrão: 30)
- **Comportamento**:
  - Ativa o timer
  - Registra o tempo de início
  - Configura a duração da rodada

### Monitorar tempo restante
- **Endpoint**: `GET /api/tempo_restante`
- **Descrição**: Verifica quanto tempo resta na rodada atual.
- **Comportamento**:
  - Calcula o tempo decorrido desde o início
  - Se o tempo acabou, desativa o timer automaticamente
  - Retorna o tempo restante e status do timer

### Enviar resposta do jogador
- **Endpoint**: `POST /api/enviar_resposta`
- **Descrição**: Registra a resposta de um jogador.
- **Parâmetros**:
  - `jogador_id`: ID do jogador respondente
  - `opcao` ou `resposta`: Opção escolhida (A, B ou C)
  - `tempo`: Tempo de resposta em milissegundos (opcional)
- **Comportamento**:
  - Verifica se a resposta está correta
  - Calcula a pontuação com base no tempo de resposta
  - Atualiza a pontuação do jogador

## 4. Finalização do Jogo

### Verificação automática de fim de jogo
- **Endpoint**: `GET /api/verificar_fim_jogo`
- **Descrição**: Verifica se o jogo foi concluído e identifica o vencedor.
- **Comportamento**:
  - Verifica se `rodada_atual > total_rodadas`
  - Se sim, atualiza o estado para "finalizado"
  - Identifica o vencedor pela maior pontuação
  - Retorna status do jogo e dados do vencedor

### Obter resultados finais
- **Endpoint**: `GET /api/resultados`
- **Descrição**: Obtém a classificação final dos jogadores.
- **Resposta**:
  ```json
  {
    "status": "finalizado",
    "rodada_atual": 4,
    "total_rodadas": 3,
    "classificacao": [
      {"id": 3, "nome": "Jogador 3", "pontuacao": 25},
      {"id": 1, "nome": "Jogador 1", "pontuacao": 18},
      {"id": 2, "nome": "Jogador 2", "pontuacao": 12}
    ]
  }
  ```

## 5. Reinício ou Nova Partida

### Reiniciar com os mesmos jogadores
- **Endpoint**: `POST /api/reiniciar`
- **Descrição**: Reinicia o jogo mantendo os mesmos jogadores.
- **Comportamento**:
  - Mantém a lista de participantes
  - Zera as pontuações
  - Reseta o estado para "aguardando"
  - Zera a rodada atual

### Voltar para modo apresentação
- **Endpoint**: `POST /api/modo_apresentacao`
- **Descrição**: Coloca o jogo em modo de espera/apresentação.
- **Comportamento**:
  - Muda o estado para "apresentacao"
  - Exibe mensagem personalizada 
  - Prepara o sistema para um novo ciclo de jogo

## Implementação de Sequências

Para criar uma experiência mais interativa, recomenda-se implementar sequências no Chataigne para cada transição de estado:

### 1. Sequência de Inicialização
- Aciona efeitos visuais no Resolume para introduzir o jogo
- Faz chamada à API (`/api/iniciar`)
- Apresenta os jogadores
- Exibe regras do jogo

### 2. Sequência de Nova Rodada
- Toca efeito sonoro de transição
- Faz chamada à API (`/api/proxima_rodada`)
- Em seguida, obtém a pergunta (`/api/pergunta_atual`)
- Anima a entrada da pergunta no Resolume
- Inicia o timer (`/api/iniciar_timer`)

### 3. Sequência de Tempo Esgotado
- Dispara quando o timer chega a zero
- Toca efeito sonoro de alerta
- Revela a resposta correta
- Prepara transição para próxima rodada

### 4. Sequência de Finalização
- Reconhece o fim do jogo
- Chama `/api/resultados` para obter classificação
- Anima a exibição da classificação
- Destaca o vencedor com efeitos visuais e sonoros

### 5. Sequência de Reinício/Apresentação
- Oferece opções para reiniciar ou voltar ao início
- Chama `/api/reiniciar` ou `/api/modo_apresentacao`
- Transição visual para o estado escolhido

## Recomendações para Implementação

1. **Tratamento de Erros**: Implementar verificações em cada transição para garantir que o estado atual permite a próxima ação.

2. **Feedback Visual**: Cada estado deve ter um visual distintivo para que os usuários saibam onde estão no ciclo do jogo.

3. **Monitoramento Automático**: Considerar a implementação de verificações periódicas do estado do jogo para detectar automaticamente transições.

4. **Logs Detalhados**: Manter logs de todas as transições para facilitar a depuração.

5. **Temporizadores**: Além do timer da rodada, considerar temporizadores para transições automáticas entre estados (ex: modo apresentação após 60 segundos de inatividade). 