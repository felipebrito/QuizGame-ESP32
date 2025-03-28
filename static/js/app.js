// Constantes da API
const API_BASE_URL = '/api';
const API_ENDPOINTS = {
    // Status
    STATUS: `${API_BASE_URL}/status`,
    // Gestão de jogadores
    PLAYERS: `${API_BASE_URL}/jogadores`,
    PLAYER: `${API_BASE_URL}/jogador`,
    REGISTER_PLAYER: `${API_BASE_URL}/cadastrar_jogador`,
    UPDATE_PLAYER: `${API_BASE_URL}/atualizar_jogador`,
    REMOVE_PLAYER: `${API_BASE_URL}/remover_jogador`,
    // Configuração
    SELECTION_MODE: `${API_BASE_URL}/modo_selecao`,
    CONFIGURATION: `${API_BASE_URL}/configuracao`,
    CONFIGURE_GAME: `${API_BASE_URL}/configurar_partida`,
    AVAILABLE_PLAYERS: `${API_BASE_URL}/jogadores_disponiveis`,
    SELECTED_PLAYERS: `${API_BASE_URL}/jogadores_selecionados`,
    UNSELECTED_PLAYERS: `${API_BASE_URL}/jogadores_nao_selecionados`,
    // Controle da partida
    WAIT: `${API_BASE_URL}/aguardar`,
    START_GAME: `${API_BASE_URL}/iniciar_partida`,
    START_ROUND: `${API_BASE_URL}/iniciar_rodada`,
    FINALIZE_ROUND: `${API_BASE_URL}/finalizar_rodada`,
    // Informações
    GAME: `${API_BASE_URL}/partida`,
    ROUND: `${API_BASE_URL}/rodada`,
    TIMER: `${API_BASE_URL}/timer`,
    PARTICIPANTS: `${API_BASE_URL}/participantes`,
    RANKING: `${API_BASE_URL}/ranking`,
    HISTORY: `${API_BASE_URL}/historico`,
    // Resultados
    WINNERS: `${API_BASE_URL}/jogadores_vencedores`,
    LOSERS: `${API_BASE_URL}/jogadores_perdedores`,
    // Utilitários
    RESET: `${API_BASE_URL}/reset`
};

// Estados do jogo
const GAME_STATES = {
    PRESENTATION: 'apresentacao',
    SELECTION: 'selecao',
    WAITING: 'aguardando',
    STARTED: 'iniciada',
    ACTIVE_ROUND: 'rodada_ativa',
    FINALIZED: 'finalizada'
};

// App Vue
const app = Vue.createApp({
    data() {
        return {
            // Estado do jogo
            gameStatus: GAME_STATES.PRESENTATION,
            gameStarted: false,
            roundActive: false,
            
            // Alerta de status
            statusAlert: {
                show: false,
                type: 'alert-info',
                title: '',
                message: ''
            },
            
            // Jogadores
            players: [],
            availablePlayers: [],
            selectedPlayerIds: [],
            participants: [],
            ranking: [],
            
            // Modal de jogador
            playerForm: {
                nome: '',
                foto: ''
            },
            editingPlayer: null,
            editingPlayerId: null,
            
            // Configuração
            configuration: {
                duracao_rodada: 30,
                total_rodadas: 10,
                tema: 'default',
                jogadores_selecionados: []
            },
            
            // Timer
            timerDisplay: '00:00',
            timerPercent: 0,
            timerClass: 'bg-success',
            
            // Rodada
            currentRound: 0,
            totalRounds: 0,
            roundPoints: {},
            
            // Visualização atual
            currentInfoDisplay: '',
            
            // Polling
            pollingTimer: null,
            pollingInterval: 1000
        };
    },
    computed: {
        // Botões de controle
        canReset() {
            return true; // Reset sempre disponível
        },
        canEnterSelection() {
            return this.gameStatus === GAME_STATES.PRESENTATION;
        },
        canWait() {
            return this.gameStatus === GAME_STATES.SELECTION;
        },
        canStartGame() {
            return this.gameStatus === GAME_STATES.WAITING;
        },
        canStartRound() {
            return this.gameStatus === GAME_STATES.STARTED;
        },
        canFinalizeRound() {
            return this.gameStatus === GAME_STATES.ACTIVE_ROUND;
        }
    },
    mounted() {
        // Carregar o estado inicial
        this.getStatus();
        
        // Iniciar polling
        this.startPolling();
    },
    beforeUnmount() {
        // Limpar polling ao desmontar
        this.stopPolling();
    },
    methods: {
        // Polling
        startPolling() {
            this.pollingTimer = setInterval(() => {
                this.getStatus();
                
                if (this.gameStatus === GAME_STATES.ACTIVE_ROUND) {
                    this.getTimer();
                }
            }, this.pollingInterval);
        },
        stopPolling() {
            if (this.pollingTimer) {
                clearInterval(this.pollingTimer);
                this.pollingTimer = null;
            }
        },
        
        // Utilitários
        showAlert(type, title, message, timeout = 5000) {
            this.statusAlert = {
                show: true,
                type: `alert-${type}`,
                title: title,
                message: message
            };
            
            // Auto-ocultar após timeout
            setTimeout(() => {
                this.statusAlert.show = false;
            }, timeout);
        },
        formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        },
        
        // ---- API Calls ----
        
        // Status e Informações
        async getStatus() {
            try {
                const response = await axios.get(API_ENDPOINTS.STATUS);
                this.gameStatus = response.data.status;
                
                // Atualizar estados auxiliares
                this.gameStarted = ['aguardando', 'iniciada', 'rodada_ativa', 'finalizada'].includes(this.gameStatus);
                this.roundActive = this.gameStatus === 'rodada_ativa';
                
                // Carregar dados relevantes com base no estado
                if (this.gameStatus === GAME_STATES.PRESENTATION) {
                    this.loadPlayers();
                } else if (this.gameStatus === GAME_STATES.SELECTION) {
                    this.loadConfiguration();
                } else if (this.gameStarted) {
                    this.getParticipants();
                    this.getRanking();
                }
            } catch (error) {
                console.error('Erro ao obter status:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível obter o status do jogo.');
            }
        },
        async getGameInfo() {
            try {
                const response = await axios.get(API_ENDPOINTS.GAME);
                this.currentInfoDisplay = JSON.stringify(response.data, null, 2);
                this.currentRound = response.data.rodada_atual || 0;
                this.totalRounds = response.data.total_rodadas || 0;
            } catch (error) {
                console.error('Erro ao obter informações da partida:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível obter informações da partida.');
            }
        },
        async getRoundInfo() {
            try {
                const response = await axios.get(API_ENDPOINTS.ROUND);
                this.currentInfoDisplay = JSON.stringify(response.data, null, 2);
            } catch (error) {
                console.error('Erro ao obter informações da rodada:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível obter informações da rodada.');
            }
        },
        async getTimer() {
            try {
                const response = await axios.get(API_ENDPOINTS.TIMER);
                
                if (response.data.timer_ativo) {
                    const remainingTime = response.data.tempo_restante;
                    const totalTime = response.data.duracao_total;
                    
                    this.timerDisplay = this.formatTime(remainingTime);
                    this.timerPercent = Math.round((remainingTime / totalTime) * 100);
                    
                    // Mudar a cor da barra de progresso com base no tempo restante
                    if (this.timerPercent > 60) {
                        this.timerClass = 'bg-success';
                    } else if (this.timerPercent > 30) {
                        this.timerClass = 'bg-warning';
                    } else {
                        this.timerClass = 'bg-danger';
                    }
                } else {
                    this.timerDisplay = '00:00';
                    this.timerPercent = 0;
                }
            } catch (error) {
                console.error('Erro ao obter timer:', error);
            }
        },
        async getParticipants() {
            try {
                const response = await axios.get(API_ENDPOINTS.PARTICIPANTS);
                this.participants = response.data.participantes || [];
            } catch (error) {
                console.error('Erro ao obter participantes:', error);
            }
        },
        async getRanking() {
            try {
                const response = await axios.get(API_ENDPOINTS.RANKING);
                this.ranking = response.data.ranking || [];
            } catch (error) {
                console.error('Erro ao obter ranking:', error);
            }
        },
        async getHistory() {
            try {
                const response = await axios.get(API_ENDPOINTS.HISTORY);
                this.currentInfoDisplay = JSON.stringify(response.data, null, 2);
            } catch (error) {
                console.error('Erro ao obter histórico:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível obter o histórico do jogo.');
            }
        },
        
        // Gerenciamento de Jogadores
        async loadPlayers() {
            try {
                const response = await axios.get(API_ENDPOINTS.PLAYERS);
                this.players = response.data.jogadores || [];
            } catch (error) {
                console.error('Erro ao carregar jogadores:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível carregar os jogadores.');
            }
        },
        showAddPlayerModal() {
            this.editingPlayer = null;
            this.editingPlayerId = null;
            this.playerForm = {
                nome: '',
                foto: 'https://randomuser.me/api/portraits/lego/1.jpg'
            };
            
            const playerModal = new bootstrap.Modal(document.getElementById('playerModal'));
            playerModal.show();
        },
        editPlayer(player) {
            this.editingPlayer = player;
            this.editingPlayerId = player.id;
            this.playerForm = {
                nome: player.nome,
                foto: player.foto
            };
            
            const playerModal = new bootstrap.Modal(document.getElementById('playerModal'));
            playerModal.show();
        },
        async savePlayer() {
            try {
                let response;
                
                if (this.editingPlayer) {
                    // Atualizar jogador existente
                    response = await axios.put(`${API_ENDPOINTS.UPDATE_PLAYER}/${this.editingPlayerId}`, this.playerForm);
                    this.showAlert('success', 'Sucesso!', 'Jogador atualizado com sucesso.');
                } else {
                    // Cadastrar novo jogador
                    response = await axios.post(API_ENDPOINTS.REGISTER_PLAYER, this.playerForm);
                    this.showAlert('success', 'Sucesso!', 'Jogador cadastrado com sucesso.');
                }
                
                // Fechar o modal
                const playerModal = bootstrap.Modal.getInstance(document.getElementById('playerModal'));
                playerModal.hide();
                
                // Atualizar a lista de jogadores
                this.loadPlayers();
            } catch (error) {
                console.error('Erro ao salvar jogador:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível salvar o jogador.');
            }
        },
        async deletePlayer(playerId) {
            if (!confirm('Tem certeza que deseja remover este jogador?')) {
                return;
            }
            
            try {
                await axios.delete(`${API_ENDPOINTS.REMOVE_PLAYER}/${playerId}`);
                this.showAlert('success', 'Sucesso!', 'Jogador removido com sucesso.');
                
                // Atualizar a lista de jogadores
                this.loadPlayers();
            } catch (error) {
                console.error('Erro ao remover jogador:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível remover o jogador.');
            }
        },
        
        // Configuração da Partida
        async loadConfiguration() {
            try {
                // Obter a configuração atual
                const configResponse = await axios.get(API_ENDPOINTS.CONFIGURATION);
                this.configuration = configResponse.data.configuracao || this.configuration;
                this.selectedPlayerIds = this.configuration.jogadores_selecionados || [];
                
                // Obter jogadores disponíveis
                const availableResponse = await axios.get(API_ENDPOINTS.AVAILABLE_PLAYERS);
                this.availablePlayers = availableResponse.data.jogadores_disponiveis || [];
            } catch (error) {
                console.error('Erro ao carregar configuração:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível carregar a configuração.');
            }
        },
        async saveConfiguration() {
            try {
                // Atualizar a configuração
                const config = {
                    jogadores: this.selectedPlayerIds,
                    duracao_rodada: parseFloat(this.configuration.duracao_rodada),
                    total_rodadas: parseInt(this.configuration.total_rodadas),
                    tema: this.configuration.tema
                };
                
                // Enviar para a API
                const response = await axios.post(API_ENDPOINTS.CONFIGURE_GAME, config);
                
                this.showAlert('success', 'Sucesso!', 'Configuração salva com sucesso.');
                this.loadConfiguration(); // Recarregar para confirmar as mudanças
            } catch (error) {
                console.error('Erro ao salvar configuração:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível salvar a configuração.');
            }
        },
        
        // Controle do Jogo
        async resetGame() {
            try {
                await axios.post(API_ENDPOINTS.RESET);
                this.showAlert('info', 'Reset!', 'O jogo foi reiniciado com sucesso.');
                this.getStatus(); // Atualizar o estado
            } catch (error) {
                console.error('Erro ao resetar o jogo:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível resetar o jogo.');
            }
        },
        async enterSelectionMode() {
            try {
                await axios.post(API_ENDPOINTS.SELECTION_MODE);
                this.showAlert('success', 'Modo Seleção!', 'Você entrou no modo de seleção de jogadores.');
                this.getStatus(); // Atualizar o estado
            } catch (error) {
                console.error('Erro ao entrar no modo seleção:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível entrar no modo seleção.');
            }
        },
        async waitForStart() {
            try {
                await axios.post(API_ENDPOINTS.WAIT);
                this.showAlert('warning', 'Aguardando!', 'O jogo está aguardando para iniciar.');
                this.getStatus(); // Atualizar o estado
            } catch (error) {
                console.error('Erro ao aguardar início:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível aguardar o início do jogo.');
            }
        },
        async startGame() {
            try {
                await axios.post(API_ENDPOINTS.START_GAME);
                this.showAlert('info', 'Partida Iniciada!', 'A partida foi iniciada com sucesso.');
                this.getStatus(); // Atualizar o estado
            } catch (error) {
                console.error('Erro ao iniciar partida:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível iniciar a partida.');
            }
        },
        async startRound() {
            try {
                await axios.post(API_ENDPOINTS.START_ROUND);
                this.showAlert('info', 'Rodada Iniciada!', 'A rodada foi iniciada com sucesso.');
                this.getStatus(); // Atualizar o estado
            } catch (error) {
                console.error('Erro ao iniciar rodada:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível iniciar a rodada.');
            }
        },
        showFinalizeRound() {
            // Inicializar pontos como zero para todos os participantes
            this.roundPoints = {};
            this.participants.forEach(player => {
                this.roundPoints[player.id] = 0;
            });
            
            // Mostrar o modal
            const finalizeRoundModal = new bootstrap.Modal(document.getElementById('finalizeRoundModal'));
            finalizeRoundModal.show();
        },
        async finalizeRound() {
            try {
                // Enviar para a API
                await axios.post(API_ENDPOINTS.FINALIZE_ROUND, { pontos: this.roundPoints });
                
                // Fechar o modal
                const finalizeRoundModal = bootstrap.Modal.getInstance(document.getElementById('finalizeRoundModal'));
                finalizeRoundModal.hide();
                
                this.showAlert('success', 'Rodada Finalizada!', 'A rodada foi finalizada com sucesso.');
                this.getStatus(); // Atualizar o estado
                
                // Atualizar ranking
                if (this.gameStatus !== GAME_STATES.FINALIZED) {
                    this.getRanking();
                }
            } catch (error) {
                console.error('Erro ao finalizar rodada:', error);
                this.showAlert('danger', 'Erro!', 'Não foi possível finalizar a rodada.');
            }
        }
    }
});

// Montar o app Vue
app.mount('#app'); 