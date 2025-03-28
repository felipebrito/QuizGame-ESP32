# Roadmap do Projeto Quiz Game

## Visão Geral
Este documento detalha as etapas de desenvolvimento do sistema Quiz Game, incluindo hardware (ESP32) e software (Chataigne, API REST e Resolume).

## Etapas Concluídas

### Hardware - ESP32
- [x] Implementação do ESP32 com comunicação WebSocket (QuizGame_v1.0)
  - [x] Configuração de comunicação WebSocket
  - [x] Detecção de botões para 3 jogadores
  - [x] Envio de mensagens formatadas em JSON
  - [x] Documentação da montagem física

- [x] Implementação do ESP32 com protocolo ESP-NOW (QuizGame_v2.0)
  - [x] Configuração do ESP32 Master para comunicação com PCs
  - [x] Configuração de ESP32 Clients para botões dos jogadores
  - [x] Comunicação Serial com o computador
  - [x] Formato de mensagens simplificado

### Software - API REST
- [x] Criação da API REST em Flask
  - [x] Endpoint raiz (/) com documentação da API
  - [x] Endpoint de status (/api/status)
  - [x] Endpoint para iniciar jogo (/api/iniciar)
  - [x] Endpoint para próxima rodada (/api/proxima_rodada)
  - [x] Endpoint para obter pergunta atual (/api/pergunta_atual)
  - [x] Endpoint para enviar resposta (/api/enviar_resposta)
  - [x] Endpoint para obter resultados (/api/resultados)
  - [x] Implementação do timer com reset automático
  - [x] Endpoints para controle do timer (/api/iniciar_timer, /api/tempo_restante, /api/cancelar_timer)

### Software - Chataigne
- [x] Integração com API REST
  - [x] Configuração do módulo HTTP
  - [x] Script para comunicação com a API
  - [x] Variáveis customizadas para armazenar estados
  - [x] Botões para controle do jogo
  - [x] Integração com ESP32 via Serial ou WebSocket
  - [x] Monitoramento do tempo restante
  - [x] Implementação do timer com atualização periódica

- [x] Integração com Resolume
  - [x] Configuração do módulo OSC
  - [x] Script para envio de perguntas e respostas
  - [x] Script para envio de estado do jogo
  - [x] Exibição do timer na tela

## Próximas Etapas

### Melhorias na API
- [ ] Implementação de banco de dados para perguntas e respostas
- [ ] Sistema de importação/exportação de perguntas (CSV/JSON)
- [ ] API para gerenciamento de jogadores (adicionar/remover)
- [ ] Estatísticas detalhadas por jogador e rodada
- [ ] Sistema de pontuação configurável

### Melhorias no Chataigne
- [ ] Sequência para animação de início de jogo
- [ ] Sequência para transição entre perguntas
- [ ] Sequência para animação de tempo esgotado
- [ ] Sequência para exibição de resultados
- [ ] Dashboard com status em tempo real

### Melhorias no Resolume
- [ ] Template completo com animações para perguntas
- [ ] Sistema de cores diferentes para cada jogador
- [ ] Animações para tempo esgotado
- [ ] Efeitos visuais para respostas corretas/incorretas
- [ ] Tela de placar com animações

### Documentação
- [ ] Manual de usuário completo
- [ ] Tutorial em vídeo para configuração
- [ ] Diagramas de arquitetura do sistema
- [ ] Documentação técnica detalhada da API

## Marcos (Milestones)

### Milestone 1: MVP Funcional ✅
Sistema básico funcionando com ESP32, API REST, Chataigne e Resolume.

### Milestone 2: Experiência do Usuário Aprimorada 🔄
Adição de animações, sequências e melhorias visuais.

### Milestone 3: Gestão Avançada de Conteúdo
Sistema completo para gerenciamento de perguntas, jogadores e estatísticas.

### Milestone 4: Produto Final
Sistema otimizado, documentado e pronto para uso em produções.

## Notas Adicionais
- Prioridade atual: Milestone 2 - Melhorar a experiência visual e interativa do jogo
- Considerar a adição de efeitos sonoros sincronizados com eventos do jogo
- Explorar a possibilidade de integração com streaming para transmissão ao vivo 