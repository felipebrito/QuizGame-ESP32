# Próximos Passos - Quiz Game

Este documento detalha os próximos passos e tarefas prioritárias para o desenvolvimento do sistema Quiz Game, considerando o estado atual do projeto.

## Status Atual

O sistema possui uma base funcional com:
- Hardware ESP32 nas versões WebSocket e ESP-NOW
- API REST em Flask com gerenciamento básico do jogo
- Integração com Chataigne para controle
- Comunicação com Resolume para visualização
- Timer funcionando com reset automático

## Prioridades Imediatas (Milestone 2)

### 1. Melhorias na Experiência Visual

#### Sequências no Chataigne
- [ ] **Sequência de Início de Jogo**
  - Desenvolver uma sequência que combine:
    - Animação de abertura
    - Apresentação dos jogadores
    - Reset de variáveis do jogo
    - Música de abertura

- [ ] **Sequência de Transição entre Perguntas**
  - Criar uma sequência que:
    - Mostre uma animação de transição
    - Exiba o tema da próxima pergunta
    - Prepare a tela para a nova pergunta

- [ ] **Sequência de Tempo Esgotado**
  - Implementar efeitos quando o timer chega a zero:
    - Alerta visual
    - Som de alarme
    - Destacar a resposta correta

- [ ] **Sequência de Exibição de Resultados**
  - Criar uma apresentação dinâmica:
    - Revelar pontuações em ordem
    - Destacar o vencedor
    - Mostrar estatísticas da partida

#### Animações no Resolume
- [ ] **Template de Perguntas Aprimorado**
  - Desenvolver uma interface que:
    - Utilize um design mais elaborado
    - Inclua uma área para o timer
    - Destaque a pergunta atual
    - Anime a entrada das opções de resposta

- [ ] **Indicadores de Jogadores**
  - Implementar sistema visual para:
    - Identificar cada jogador por cor
    - Mostrar quando um jogador respondeu
    - Revelar a opção selecionada após o tempo

### 2. Melhorias na Lógica do Jogo

- [ ] **Sistema de Pontuação Proporcional ao Tempo**
  - Implementar na API:
    - Cálculo de pontos baseado no tempo restante
    - Bônus para respostas rápidas
    - Penalidade para respostas erradas

- [ ] **Modos de Jogo**
  - Adicionar opções como:
    - Modo rápido (5 segundos por pergunta)
    - Modo desafio (perguntas mais difíceis)
    - Modo eliminação (jogador com menor pontuação sai)

### 3. Melhorias na Interface de Controle

- [ ] **Dashboard em Chataigne**
  - Criar um painel que mostre em tempo real:
    - Estado do jogo
    - Pontuação dos jogadores
    - Resposta dada por cada jogador
    - Tempo restante visual

- [ ] **Controles Avançados**
  - Implementar:
    - Botão para pausar o jogo
    - Opção para anular uma rodada
    - Sistema para ajustar a dificuldade

## Próximos Milestones

### Milestone 3: Gestão Avançada de Conteúdo

- [ ] **Banco de Dados para Perguntas**
  - Migrar de dados estáticos para um banco SQLite
  - Implementar CRUD completo de perguntas

- [ ] **Sistema de Importação/Exportação**
  - Permitir carregar perguntas a partir de CSV/JSON
  - Exportar resultados de partidas

- [ ] **API para Gerenciamento de Jogadores**
  - Endpoints para adicionar/remover jogadores
  - Persistência de dados dos jogadores

- [ ] **Interface Admin Web**
  - Criar uma interface simples para:
    - Gerenciar perguntas
    - Configurar jogos
    - Visualizar estatísticas

### Milestone 4: Produto Final

- [ ] **Documentação Completa**
  - Manual do usuário detalhado
  - Tutorial em vídeo
  - Diagrama técnico

- [ ] **Otimização de Performance**
  - Revisão do código para melhorar eficiência
  - Teste em condições de produção

- [ ] **Empacotamento**
  - Distribuir como solução completa
  - Instalador/script de configuração

## Fluxo de Trabalho Recomendado

1. Começar implementando as sequências em Chataigne
2. Preparar o template visual no Resolume
3. Conectar sequências a eventos do jogo
4. Testar a experiência completa
5. Refinar a pontuação e mecânicas do jogo
6. Avançar para o sistema de banco de dados

Este plano está alinhado com o objetivo de criar uma experiência de jogo mais interativa e visualmente atraente, antes de adicionar funcionalidades avançadas de gerenciamento de conteúdo. 