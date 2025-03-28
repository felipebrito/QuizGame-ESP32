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

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

Documentação atualizada em 28/03/2025.

# API Quiz Game

API para gerenciamento de um jogo de quiz multiplayer interativo.

## Visão Geral

Esta API permite criar e gerenciar partidas de quiz, com suporte a múltiplos jogadores, rodadas configuráveis, e sistema de pontuação. A API é construída em Flask e oferece endpoints para todas as funcionalidades necessárias para um jogo de quiz completo.

## Estados do Jogo

O jogo possui os seguintes estados:

- **apresentacao**: Modo inicial, exibindo ranking e aguardando início de partida
- **selecao**: Seleção de jogadores e configuração da partida
- **iniciada**: Partida iniciada, pronta para começar as rodadas
- **abertura**: Abertura de uma nova rodada (countdown)
- **rodada_ativa**: Rodada em andamento com pergunta ativa
- **finalizada**: Partida finalizada, exibindo pontuações e vencedores

## Fluxo do Jogo

O fluxo correto para uma partida é:

1. `/api/modo_apresentacao` - Iniciar em modo apresentação (tela inicial)
2. `/api/nova_partida` - Criar nova partida (resetar estado)
3. `/api/modo_selecao` - Entrar no modo de seleção de jogadores
4. `/api/configurar_partida` - Configurar jogadores, rodadas e tempo
5. `/api/iniciar_partida` - Iniciar a partida configurada
6. Para cada rodada:
   - `/api/abertura_rodada` - Iniciar abertura para a próxima rodada
   - `/api/iniciar_rodada` - Iniciar a rodada com a pergunta
   - `/api/enviar_resposta` - Jogadores enviam respostas
   - `/api/verificar_avancar` - Verificar se pode avançar para próxima rodada
7. Ao final, retornar ao modo apresentação

## Endpoints da API

### Configuração e Estado do Jogo

- `GET /api/status` - Retorna o estado atual do jogo com todos os detalhes
- `POST /api/modo_apresentacao` - Coloca o jogo em modo apresentação (tela inicial)
- `POST /api/nova_partida` - Cria uma nova partida, resetando o estado do jogo
- `POST /api/modo_selecao` - Ativa o modo de seleção de jogadores
- `POST /api/configurar_partida` - Configura detalhes da partida (jogadores, rodadas, tempo)
- `POST /api/iniciar_partida` - Inicia a partida configurada

### Gerenciamento de Rodadas

- `POST /api/abertura_rodada` - Inicia abertura para a próxima rodada (countdown)
- `POST /api/iniciar_rodada` - Inicia uma rodada com pergunta
- `POST /api/enviar_resposta` - Recebe resposta de um jogador
- `GET /api/verificar_avancar` - Verifica se pode avançar para próxima rodada
- `GET /api/pergunta_atual` - Obtém a pergunta atual da rodada

### Gerenciamento de Jogadores

- `POST /api/cadastrar_jogador` - Cadastra um novo jogador
- `GET /api/jogadores` - Lista todos os jogadores cadastrados
- `GET /api/jogadores_disponiveis` - Lista jogadores disponíveis para seleção
- `DELETE /api/remover_jogador/<id>` - Remove um jogador cadastrado
- `PUT /api/atualizar_jogador/<id>` - Atualiza dados de um jogador

### Verificação de Estado

- `GET /api/status_selecao` - Verifica status do modo seleção
- `GET /api/status_rodada` - Verifica status da rodada atual
- `GET /api/respostas_rodada` - Obtém respostas da rodada atual
- `GET /api/ranking` - Obtém ranking atual da partida

## Formatos de Requisição e Resposta

### Configurar Partida

**Requisição:**
```json
{
  "jogadores": [1, 2, 3],
  "duracao_rodada": 30,
  "total_rodadas": 10,
  "tema": "default"
}
```

**Resposta:**
```json
{
  "configuracao": {
    "duracao_rodada": 30.0,
    "jogadores_selecionados": [1, 2, 3],
    "status": "validada",
    "tema": "default",
    "total_rodadas": 10
  },
  "mensagem": "Configuração da partida atualizada com sucesso"
}
```

### Enviar Resposta

**Requisição:**
```json
{
  "jogador": "1",
  "resposta": "A",
  "tempo": "5.2"
}
```

**Resposta:**
```json
{
  "mensagem": "Resposta registrada com sucesso",
  "resposta_registrada": true
}
```

## Detalhes Importantes

1. O campo `texto_proxima_rodada` no endpoint `/api/abertura_rodada` exibirá "FINAL" quando for a última rodada.
2. O campo `texto_rodada_atual` no endpoint `/api/iniciar_rodada` exibirá "FINAL" quando for a última rodada.
3. Para obter informações sobre a próxima rodada, use exclusivamente o endpoint `/api/verificar_avancar`.
4. Ao iniciar uma nova partida, os estados anteriores são limpos, incluindo `texto_proxima_rodada`.

## Exemplos de Uso

### Iniciar uma nova partida

```bash
curl -X POST http://localhost:5001/api/modo_apresentacao
curl -X POST http://localhost:5001/api/nova_partida
curl -X POST http://localhost:5001/api/modo_selecao
curl -X POST -H "Content-Type: application/json" -d '{"jogadores": [1, 2, 3], "duracao_rodada": 30, "total_rodadas": 10, "tema": "default"}' http://localhost:5001/api/configurar_partida
curl -X POST http://localhost:5001/api/iniciar_partida
```

### Iniciar uma rodada

```bash
curl -X POST http://localhost:5001/api/abertura_rodada
curl -X POST http://localhost:5001/api/iniciar_rodada
```

### Enviar uma resposta

```bash
curl -X POST -H "Content-Type: application/json" -d '{"jogador": "1", "resposta": "A", "tempo": "5.2"}' http://localhost:5001/api/enviar_resposta
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 