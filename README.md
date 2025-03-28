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

# Quiz Game API

API para gerenciamento de um jogo de quiz com múltiplos jogadores.

## Funcionalidades

- Gerenciamento de jogadores (cadastro, atualização, remoção)
- Configuração de partidas (seleção de jogadores, duração, rodadas)
- Controle de rodadas (início, fim, pontuação)
- Sistema de ranking e histórico
- Timer para controle de tempo
- Estados do jogo (apresentação, selecao, aguardando, iniciada, rodada_ativa, finalizada)

## Requisitos

- Python 3.8+
- Flask
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/felipebrito/QuizGame-ESP32.git
cd QuizGame-ESP32
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o Servidor

```bash
python app.py
```

O servidor estará disponível em `http://localhost:5001`

## Endpoints da API

### Gerenciamento de Jogadores

#### Cadastrar Jogador
- **URL**: `/api/cadastrar_jogador`
- **Método**: `POST`
- **Descrição**: Cadastra um novo jogador
- **Estado**: apresentacao
- **Corpo**:
```json
{
    "nome": "Nome do Jogador",
    "foto": "URL da foto (opcional)"
}
```

#### Listar Jogadores
- **URL**: `/api/jogadores`
- **Método**: `GET`
- **Descrição**: Lista todos os jogadores cadastrados
- **Estado**: apresentacao

#### Obter Jogador
- **URL**: `/api/jogador/<id>`
- **Método**: `GET`
- **Descrição**: Retorna os dados de um jogador específico
- **Estado**: apresentacao

#### Atualizar Jogador
- **URL**: `/api/atualizar_jogador/<id>`
- **Método**: `PUT`
- **Descrição**: Atualiza os dados de um jogador
- **Estado**: apresentacao
- **Corpo**:
```json
{
    "nome": "Novo Nome",
    "foto": "Nova URL da foto"
}
```

#### Remover Jogador
- **URL**: `/api/remover_jogador/<id>`
- **Método**: `DELETE`
- **Descrição**: Remove um jogador cadastrado
- **Estado**: apresentacao

### Configuração da Partida

#### Entrar no Modo Seleção
- **URL**: `/api/modo_selecao`
- **Método**: `POST`
- **Descrição**: Entra no modo de seleção de jogadores
- **Estado**: apresentacao

#### Configurar Partida
- **URL**: `/api/configurar_partida`
- **Método**: `POST`
- **Descrição**: Configura os parâmetros da partida
- **Estado**: selecao
- **Corpo**:
```json
{
    "jogadores": [1, 2, 3],
    "duracao_rodada": 30.0,
    "total_rodadas": 10,
    "tema": "default"
}
```

#### Obter Configuração
- **URL**: `/api/configuracao`
- **Método**: `GET`
- **Descrição**: Retorna a configuração atual
- **Estado**: selecao

#### Obter Jogadores Disponíveis
- **URL**: `/api/jogadores_disponiveis`
- **Método**: `GET`
- **Descrição**: Retorna os jogadores disponíveis para seleção
- **Estado**: selecao

#### Obter Jogadores Selecionados
- **URL**: `/api/jogadores_selecionados`
- **Método**: `GET`
- **Descrição**: Retorna os jogadores selecionados
- **Estado**: selecao

#### Obter Jogadores Não Selecionados
- **URL**: `/api/jogadores_nao_selecionados`
- **Método**: `GET`
- **Descrição**: Retorna os jogadores não selecionados
- **Estado**: selecao

### Controle da Partida

#### Aguardar
- **URL**: `/api/aguardar`
- **Método**: `POST`
- **Descrição**: Aguarda o início da partida
- **Estado**: selecao

#### Iniciar Partida
- **URL**: `/api/iniciar_partida`
- **Método**: `POST`
- **Descrição**: Inicia a partida com base na configuração
- **Estado**: aguardando

#### Iniciar Rodada
- **URL**: `/api/iniciar_rodada`
- **Método**: `POST`
- **Descrição**: Inicia uma nova rodada
- **Estado**: iniciada

#### Finalizar Rodada
- **URL**: `/api/finalizar_rodada`
- **Método**: `POST`
- **Descrição**: Finaliza a rodada atual
- **Estado**: rodada_ativa
- **Corpo**:
```json
{
    "pontos": {
        "1": 10,
        "2": 5,
        "3": 0
    }
}
```

### Status e Informações

#### Obter Status
- **URL**: `/api/status`
- **Método**: `GET`
- **Descrição**: Retorna o status atual do jogo

#### Obter Partida
- **URL**: `/api/partida`
- **Método**: `GET`
- **Descrição**: Retorna o status da partida
- **Estado**: aguardando, iniciada, rodada_ativa, finalizada

#### Obter Rodada
- **URL**: `/api/rodada`
- **Método**: `GET`
- **Descrição**: Retorna o status da rodada atual
- **Estado**: rodada_ativa

#### Obter Timer
- **URL**: `/api/timer`
- **Método**: `GET`
- **Descrição**: Retorna o status do timer
- **Estado**: rodada_ativa

#### Obter Participantes
- **URL**: `/api/participantes`
- **Método**: `GET`
- **Descrição**: Retorna os participantes da partida
- **Estado**: aguardando, iniciada, rodada_ativa, finalizada

#### Obter Ranking
- **URL**: `/api/ranking`
- **Método**: `GET`
- **Descrição**: Retorna o ranking dos jogadores
- **Estado**: aguardando, iniciada, rodada_ativa, finalizada

### Resultados e Histórico

#### Obter Histórico
- **URL**: `/api/historico`
- **Método**: `GET`
- **Descrição**: Retorna o histórico do jogo
- **Estado**: apresentacao

#### Obter Jogadores Vencedores
- **URL**: `/api/jogadores_vencedores`
- **Método**: `GET`
- **Descrição**: Retorna os jogadores vencedores
- **Estado**: finalizada

#### Obter Jogadores Perdedores
- **URL**: `/api/jogadores_perdedores`
- **Método**: `GET`
- **Descrição**: Retorna os jogadores perdedores
- **Estado**: finalizada

### Utilitários

#### Reset
- **URL**: `/api/reset`
- **Método**: `POST`
- **Descrição**: Reseta o jogo para o estado inicial

## Estados do Jogo

1. **apresentacao**
   - Estado inicial
   - Permite cadastro e gerenciamento de jogadores
   - Permite visualizar histórico

2. **selecao**
   - Permite selecionar jogadores e configurar parâmetros
   - Permite visualizar jogadores disponíveis e selecionados

3. **aguardando**
   - Aguarda confirmação para iniciar a partida
   - Permite visualizar configuração e participantes

4. **iniciada**
   - Partida em andamento
   - Permite iniciar rodadas
   - Permite visualizar ranking e participantes

5. **rodada_ativa**
   - Rodada em andamento
   - Timer ativo
   - Permite finalizar rodada

6. **finalizada**
   - Partida concluída
   - Permite visualizar resultados e histórico

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 