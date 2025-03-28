from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time  # Importando o módulo time para controle do timer
import os  # Importando o módulo os para matar processos
import random  # Importando o módulo random para embaralhar perguntas

app = Flask(__name__, static_folder='static', template_folder='templates')
app.jinja_env.variable_start_string = '{['  # Alterando de {{ para {[
app.jinja_env.variable_end_string = ']}'    # Alterando de }} para ]}
CORS(app)  # Permite requisições cross-origin

# Rota para a interface de gerenciamento
@app.route('/gerenciador', methods=['GET'])
def gerenciador():
    return render_template('index.html')

# Página inicial da API
@app.route('/', methods=['GET'])
def index():
    # Lista de endpoints disponíveis
    endpoints = {
        "endpoints": [
            {
                "url": "/api/status",
                "method": "GET",
                "description": "Retorna o status atual do jogo"
            },
            {
                "url": "/api/iniciar",
                "method": "POST",
                "description": "Inicia um novo jogo"
            },
            {
                "url": "/api/proxima_rodada",
                "method": "POST",
                "description": "Avança para a próxima rodada"
            },
            {
                "url": "/api/pergunta_atual",
                "method": "GET",
                "description": "Retorna a pergunta da rodada atual"
            },
            {
                "url": "/api/enviar_resposta",
                "method": "POST",
                "description": "Envia resposta de um jogador",
                "body": {
                    "jogador_id": "ID do jogador (int)",
                    "resposta": "Opção de resposta (A, B ou C)",
                    "tempo": "Tempo de resposta em ms (opcional)"
                }
            },
            {
                "url": "/api/resultados",
                "method": "GET",
                "description": "Retorna os resultados e classificação"
            },
            {
                "url": "/api/iniciar_timer",
                "method": "POST",
                "description": "Inicia o timer da rodada"
            },
            {
                "url": "/api/tempo_restante",
                "method": "GET",
                "description": "Retorna o tempo restante da rodada"
            },
            {
                "url": "/api/cancelar_timer",
                "method": "POST",
                "description": "Cancela o timer da rodada"
            },
            {
                "url": "/api/reiniciar",
                "method": "POST",
                "description": "Reinicia o jogo após finalizado"
            },
            {
                "url": "/api/modo_apresentacao",
                "method": "POST",
                "description": "Coloca o jogo em modo de apresentação/espera e exibe ranking",
                "body": {
                    "mensagem": "Mensagem personalizada (opcional)",
                    "tema": "Tema visual (opcional)"
                }
            },
            {
                "url": "/api/status_apresentacao",
                "method": "GET",
                "description": "Retorna o status do modo apresentação com ranking"
            },
            {
                "url": "/api/temas",
                "method": "GET",
                "description": "Lista os temas disponíveis"
            },
            {
                "url": "/api/verificar_fim_jogo",
                "method": "GET",
                "description": "Verifica se o jogo acabou"
            },
            {
                "url": "/api/configurar_jogadores",
                "method": "POST",
                "description": "Configura os jogadores antes de iniciar a partida",
                "body": {
                    "jogadores": "Lista de jogadores"
                }
            },
            {
                "url": "/api/modo_selecao",
                "method": "POST",
                "description": "Entra no modo de seleção"
            },
            {
                "url": "/api/configurar_partida",
                "method": "POST",
                "description": "Configura os parâmetros da partida"
            },
            {
                "url": "/api/status_selecao",
                "method": "GET",
                "description": "Retorna o status da configuração"
            },
            {
                "url": "/api/iniciar_partida",
                "method": "POST",
                "description": "Inicia a partida com base na configuração"
            },
            {
                "url": "/api/reset",
                "method": "POST",
                "description": "Reseta o jogo para o estado inicial"
            },
            {
                "url": "/api/iniciar_rodada",
                "method": "POST",
                "description": "Inicia uma nova rodada"
            },
            {
                "url": "/api/finalizar_rodada",
                "method": "POST",
                "description": "Finaliza a rodada atual"
            },
            {
                "url": "/api/aguardar",
                "method": "POST",
                "description": "Aguarda o jogo até que a configuração esteja validada"
            },
            {
                "url": "/api/cadastrar_jogador",
                "method": "POST",
                "description": "Cadastra um novo jogador"
            },
            {
                "url": "/api/jogadores",
                "method": "GET",
                "description": "Lista todos os jogadores cadastrados"
            },
            {
                "url": "/api/remover_jogador/<int:jogador_id>",
                "method": "DELETE",
                "description": "Remove um jogador cadastrado"
            },
            {
                "url": "/api/atualizar_jogador/<int:jogador_id>",
                "method": "PUT",
                "description": "Atualiza os dados de um jogador cadastrado"
            },
            {
                "url": "/api/jogador/<int:jogador_id>",
                "method": "GET",
                "description": "Retorna os dados de um jogador específico"
            },
            {
                "url": "/api/historico",
                "method": "GET",
                "description": "Retorna o histórico do jogo"
            },
            {
                "url": "/api/configuracao",
                "method": "GET",
                "description": "Retorna a configuração atual"
            },
            {
                "url": "/api/participantes",
                "method": "GET",
                "description": "Retorna os participantes da partida"
            },
            {
                "url": "/api/ranking",
                "method": "GET",
                "description": "Retorna o ranking dos jogadores"
            },
            {
                "url": "/api/timer",
                "method": "GET",
                "description": "Retorna o status do timer"
            },
            {
                "url": "/api/rodada",
                "method": "GET",
                "description": "Retorna o status da rodada atual"
            },
            {
                "url": "/api/partida",
                "method": "GET",
                "description": "Retorna o status da partida"
            },
            {
                "url": "/api/jogadores_cadastrados",
                "method": "GET",
                "description": "Retorna os jogadores cadastrados"
            },
            {
                "url": "/api/jogadores_selecionados",
                "method": "GET",
                "description": "Retorna os jogadores selecionados"
            },
            {
                "url": "/api/jogadores_disponiveis",
                "method": "GET",
                "description": "Retorna os jogadores disponíveis"
            },
            {
                "url": "/api/jogadores_nao_selecionados",
                "method": "GET",
                "description": "Retorna os jogadores não selecionados"
            },
            {
                "url": "/api/jogadores_vencedores",
                "method": "GET",
                "description": "Retorna os jogadores vencedores"
            },
            {
                "url": "/api/jogadores_perdedores",
                "method": "GET",
                "description": "Retorna os jogadores perdedores"
            },
            {
                "url": "/api/nova_partida",
                "method": "POST",
                "description": "Cria uma nova partida, colocando o jogo no modo de seleção"
            },
            {
                "url": "/api/abertura_rodada",
                "method": "POST",
                "description": "Inicia a abertura da rodada (15 segundos antes de iniciar efetivamente)"
            },
            {
                "url": "/api/status_abertura",
                "method": "GET",
                "description": "Verifica o status da abertura da rodada"
            },
            {
                "url": "/api/status_rodada",
                "method": "GET",
                "description": "Retorna o status da rodada atual"
            },
            {
                "url": "/api/respostas_rodada",
                "method": "GET",
                "description": "Retorna as respostas dos jogadores na rodada atual"
            },
            {
                "url": "/api/verificar_avancar",
                "method": "GET",
                "description": "Verifica o status da rodada e avança automaticamente se necessário"
            }
        ],
        "status": "API Quiz Game - Online",
        "version": "1.0"
    }
    
    return jsonify(endpoints)

# Dados de exemplo
todas_perguntas = [
    {
        "id": 1,
        "texto": "Qual a capital do Brasil?",
        "tema": "Geografia",
        "respostas": [
            {"opcao": "A", "texto": "Rio de Janeiro"},
            {"opcao": "B", "texto": "São Paulo"},
            {"opcao": "C", "texto": "Brasília"}
        ],
        "resposta_correta": "C"
    },
    {
        "id": 2,
        "texto": "Quem pintou a Mona Lisa?",
        "tema": "Arte",
        "respostas": [
            {"opcao": "A", "texto": "Leonardo da Vinci"},
            {"opcao": "B", "texto": "Pablo Picasso"},
            {"opcao": "C", "texto": "Vincent Van Gogh"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 3,
        "texto": "Em que ano o homem pisou na lua pela primeira vez?",
        "tema": "História",
        "respostas": [
            {"opcao": "A", "texto": "1969"},
            {"opcao": "B", "texto": "1975"},
            {"opcao": "C", "texto": "1981"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 4,
        "texto": "Qual é o maior planeta do Sistema Solar?",
        "tema": "Astronomia",
        "respostas": [
            {"opcao": "A", "texto": "Terra"},
            {"opcao": "B", "texto": "Júpiter"},
            {"opcao": "C", "texto": "Saturno"}
        ],
        "resposta_correta": "B"
    },
    {
        "id": 5,
        "texto": "Qual destes não é um elemento químico?",
        "tema": "Ciência",
        "respostas": [
            {"opcao": "A", "texto": "Hidrogênio"},
            {"opcao": "B", "texto": "Adamantium"},
            {"opcao": "C", "texto": "Oxigênio"}
        ],
        "resposta_correta": "B"
    },
    {
        "id": 6,
        "texto": "Quem escreveu 'Dom Quixote'?",
        "tema": "Literatura",
        "respostas": [
            {"opcao": "A", "texto": "Miguel de Cervantes"},
            {"opcao": "B", "texto": "William Shakespeare"},
            {"opcao": "C", "texto": "Machado de Assis"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 7,
        "texto": "Qual é o maior oceano do mundo?",
        "tema": "Geografia",
        "respostas": [
            {"opcao": "A", "texto": "Atlântico"},
            {"opcao": "B", "texto": "Índico"},
            {"opcao": "C", "texto": "Pacífico"}
        ],
        "resposta_correta": "C"
    },
    {
        "id": 8,
        "texto": "Em que ano começou a Segunda Guerra Mundial?",
        "tema": "História",
        "respostas": [
            {"opcao": "A", "texto": "1939"},
            {"opcao": "B", "texto": "1914"},
            {"opcao": "C", "texto": "1945"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 9,
        "texto": "Qual é o metal mais precioso?",
        "tema": "Ciência",
        "respostas": [
            {"opcao": "A", "texto": "Ouro"},
            {"opcao": "B", "texto": "Platina"},
            {"opcao": "C", "texto": "Prata"}
        ],
        "resposta_correta": "B"
    },
    {
        "id": 10,
        "texto": "Quem é considerado o pai da física moderna?",
        "tema": "Ciência",
        "respostas": [
            {"opcao": "A", "texto": "Isaac Newton"},
            {"opcao": "B", "texto": "Albert Einstein"},
            {"opcao": "C", "texto": "Galileu Galilei"}
        ],
        "resposta_correta": "C"
    },
    {
        "id": 11,
        "texto": "Qual é a capital do Japão?",
        "tema": "Geografia",
        "respostas": [
            {"opcao": "A", "texto": "Pequim"},
            {"opcao": "B", "texto": "Seul"},
            {"opcao": "C", "texto": "Tóquio"}
        ],
        "resposta_correta": "C"
    },
    {
        "id": 12,
        "texto": "Quem escreveu 'Romeu e Julieta'?",
        "tema": "Literatura",
        "respostas": [
            {"opcao": "A", "texto": "William Shakespeare"},
            {"opcao": "B", "texto": "Charles Dickens"},
            {"opcao": "C", "texto": "Jane Austen"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 13,
        "texto": "Qual é o país mais populoso do mundo?",
        "tema": "Geografia",
        "respostas": [
            {"opcao": "A", "texto": "Índia"},
            {"opcao": "B", "texto": "China"},
            {"opcao": "C", "texto": "Estados Unidos"}
        ],
        "resposta_correta": "B"
    },
    {
        "id": 14,
        "texto": "Quem foi o primeiro homem a pisar na Lua?",
        "tema": "História",
        "respostas": [
            {"opcao": "A", "texto": "Buzz Aldrin"},
            {"opcao": "B", "texto": "Yuri Gagarin"},
            {"opcao": "C", "texto": "Neil Armstrong"}
        ],
        "resposta_correta": "C"
    },
    {
        "id": 15,
        "texto": "Qual é a montanha mais alta do mundo?",
        "tema": "Geografia",
        "respostas": [
            {"opcao": "A", "texto": "Monte Everest"},
            {"opcao": "B", "texto": "K2"},
            {"opcao": "C", "texto": "Monte Aconcágua"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 16,
        "texto": "Quem pintou 'A Noite Estrelada'?",
        "tema": "Arte",
        "respostas": [
            {"opcao": "A", "texto": "Pablo Picasso"},
            {"opcao": "B", "texto": "Vincent Van Gogh"},
            {"opcao": "C", "texto": "Leonardo da Vinci"}
        ],
        "resposta_correta": "B"
    },
    {
        "id": 17,
        "texto": "Qual é a capital da Austrália?",
        "tema": "Geografia",
        "respostas": [
            {"opcao": "A", "texto": "Sydney"},
            {"opcao": "B", "texto": "Melbourne"},
            {"opcao": "C", "texto": "Camberra"}
        ],
        "resposta_correta": "C"
    },
    {
        "id": 18,
        "texto": "Qual é o menor planeta do Sistema Solar?",
        "tema": "Astronomia",
        "respostas": [
            {"opcao": "A", "texto": "Mercúrio"},
            {"opcao": "B", "texto": "Marte"},
            {"opcao": "C", "texto": "Vênus"}
        ],
        "resposta_correta": "A"
    },
    {
        "id": 19,
        "texto": "Qual é o maior animal terrestre?",
        "tema": "Biologia",
        "respostas": [
            {"opcao": "A", "texto": "Girafa"},
            {"opcao": "B", "texto": "Elefante africano"},
            {"opcao": "C", "texto": "Rinoceronte"}
        ],
        "resposta_correta": "B"
    },
    {
        "id": 20,
        "texto": "Quem escreveu 'Cem Anos de Solidão'?",
        "tema": "Literatura",
        "respostas": [
            {"opcao": "A", "texto": "Pablo Neruda"},
            {"opcao": "B", "texto": "Jorge Luis Borges"},
            {"opcao": "C", "texto": "Gabriel García Márquez"}
        ],
        "resposta_correta": "C"
    }
]

# Perguntas selecionadas para a partida atual
perguntas = []

# Estrutura inicial da partida
partida = {
    "status": "apresentacao",  # apresentacao, selecao, aguardando, iniciada, rodada_ativa, finalizada
    "rodada_atual": 0,
    "total_rodadas": 10,
    "timer_ativo": False,
    "tempo_inicio": 0,
    "duracao_rodada": 30.0,
    "ultima_atualizacao": time.time(),
    "configuracao": {
        "jogadores_selecionados": [],  # Lista de IDs dos jogadores selecionados
        "duracao_rodada": 30.0,       # Duração em segundos
        "total_rodadas": 10,          # Número total de rodadas
        "tema": "default",            # Tema visual da partida
        "status": "pendente"          # pendente, validada, iniciada
    },
    "ultima_partida": {
        "data": None,
        "vencedor": None,
        "pontuacao_maxima": 0
    },
    "historico": {
        "total_partidas": 0,
        "recorde_pontos": 0,
        "recordista": None
    },
    "participantes": []
}

# Estrutura de jogadores cadastrados (simulando um banco de dados)
jogadores_cadastrados = {
    "jogadores": [
        {
            "id": 1,
            "nome": "Maria Silva",
            "foto": "https://randomuser.me/api/portraits/women/42.jpg",
            "telefone": "11999999999",
            "pontuacao_total": 85,
            "partidas_jogadas": 3,
            "vitorias": 2,
            "ultima_atualizacao": time.time()
        },
        {
            "id": 2,
            "nome": "João Santos",
            "foto": "https://randomuser.me/api/portraits/men/67.jpg",
            "telefone": "11988888888",
            "pontuacao_total": 72,
            "partidas_jogadas": 3,
            "vitorias": 1,
            "ultima_atualizacao": time.time()
        },
        {
            "id": 3,
            "nome": "Ana Costa",
            "foto": "https://randomuser.me/api/portraits/women/33.jpg",
            "telefone": "11977777777",
            "pontuacao_total": 64,
            "partidas_jogadas": 3,
            "vitorias": 0,
            "ultima_atualizacao": time.time()
        },
        {
            "id": 4,
            "nome": "Pedro Oliveira",
            "foto": "https://randomuser.me/api/portraits/men/22.jpg",
            "telefone": "11966666666",
            "pontuacao_total": 95,
            "partidas_jogadas": 4,
            "vitorias": 3,
            "ultima_atualizacao": time.time()
        },
        {
            "id": 5,
            "nome": "Mariana Alves",
            "foto": "https://randomuser.me/api/portraits/women/56.jpg",
            "telefone": "11955555555",
            "pontuacao_total": 78,
            "partidas_jogadas": 3,
            "vitorias": 1,
            "ultima_atualizacao": time.time()
        }
    ]
}

# Função para selecionar perguntas aleatoriamente
def selecionar_perguntas_aleatorias():
    try:
        # Determina quantas perguntas selecionar
        total_perguntas = partida["configuracao"]["total_rodadas"]
        
        # Verifica se há perguntas suficientes no banco
        if total_perguntas > len(todas_perguntas):
            app.logger.warning(f"Total de perguntas solicitadas ({total_perguntas}) maior que o disponível ({len(todas_perguntas)}). Usando todas disponíveis.")
            perguntas_selecionadas = todas_perguntas.copy()
        else:
            # Seleciona um subconjunto aleatório das perguntas
            perguntas_selecionadas = random.sample(todas_perguntas, total_perguntas)
        
        app.logger.info(f"Selecionadas {len(perguntas_selecionadas)} perguntas aleatórias para a partida")
        return perguntas_selecionadas
    except Exception as e:
        app.logger.error(f"Erro ao selecionar perguntas aleatórias: {str(e)}")
        # Em caso de erro, retorna uma lista vazia ou todas as perguntas disponíveis
        if todas_perguntas:
            app.logger.info(f"Retornando todas as {len(todas_perguntas)} perguntas disponíveis como backup")
            return todas_perguntas.copy()
        else:
            app.logger.error("Nenhuma pergunta disponível no banco de perguntas")
            # Perguntas de emergência para garantir o funcionamento
            return [
                {
                    "id": 1,
                    "texto": "Pergunta de emergência 1",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "A"
                },
                {
                    "id": 2,
                    "texto": "Pergunta de emergência 2",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "B"
                },
                {
                    "id": 3,
                    "texto": "Pergunta de emergência 3",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "C"
                },
                {
                    "id": 4,
                    "texto": "Pergunta de emergência 4",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "D"
                },
                {
                    "id": 5,
                    "texto": "Pergunta de emergência 5",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "A"
                },
                {
                    "id": 6,
                    "texto": "Pergunta de emergência 6",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "B"
                },
                {
                    "id": 7,
                    "texto": "Pergunta de emergência 7",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "C"
                },
                {
                    "id": 8,
                    "texto": "Pergunta de emergência 8",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "D"
                },
                {
                    "id": 9,
                    "texto": "Pergunta de emergência 9",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "A"
                },
                {
                    "id": 10,
                    "texto": "Pergunta de emergência 10",
                    "tema": "Geral",
                    "respostas": [
                        {"opcao": "A", "texto": "Opção A"},
                        {"opcao": "B", "texto": "Opção B"},
                        {"opcao": "C", "texto": "Opção C"},
                        {"opcao": "D", "texto": "Opção D"}
                    ],
                    "resposta_correta": "B"
                }
            ]

@app.route('/api/status', methods=['GET'])
def status():
    # Inicializa estruturas importantes caso não existam
    if "historico" not in partida:
        partida["historico"] = {
            "total_partidas": 0,
            "recorde_pontos": 0,
            "recordista": None
        }
        
    if "ultima_partida" not in partida:
        partida["ultima_partida"] = {
            "data": None,
            "vencedor": None,
            "pontuacao_maxima": 0
        }
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    # Faz uma cópia dos dados atuais da partida
    status_atual = partida.copy()
    
    # Adiciona os jogadores disponíveis
    status_atual["jogadores_disponiveis"] = jogadores_disponiveis
    
    # Remove campos internos que não devem ser expostos
    if "perguntas_selecionadas" in status_atual:
        del status_atual["perguntas_selecionadas"]
        
    # Remove o campo proxima_rodada para evitar confusão
    if "proxima_rodada" in status_atual:
        del status_atual["proxima_rodada"]
    
    # Converte o conjunto respostas_recebidas em uma lista se existir
    if "respostas_recebidas" in status_atual and isinstance(status_atual["respostas_recebidas"], set):
        status_atual["respostas_recebidas"] = list(status_atual["respostas_recebidas"])
    
    # Calcula o tempo restante, se aplicável
    tempo_restante = 0
    if partida["timer_ativo"]:
        tempo_decorrido = time.time() - partida["tempo_inicio"]
        tempo_restante = max(0, partida["duracao_rodada"] - tempo_decorrido)
    
    # Complementa o status com informações adicionais
    status_atual["tempo_restante"] = tempo_restante
    status_atual["timer_ativo"] = partida["timer_ativo"]
    status_atual["ultima_atualizacao"] = time.time()
    
    # Adiciona texto_rodada_atual para compatibilidade com o front-end
    if partida["status"] == "rodada_ativa" or partida["status"] == "iniciada":
        rodada_atual = partida["rodada_atual"]
        total_rodadas = partida["total_rodadas"]
        
        # Se a rodada for 0 (partida iniciada mas sem nenhuma rodada ativa), exibir como 1
        if rodada_atual == 0:
            texto_rodada_atual = "1"
        # Se for a última rodada, exibir como "FINAL"
        elif rodada_atual == total_rodadas:
            texto_rodada_atual = "FINAL"
        else:
            texto_rodada_atual = str(rodada_atual)
        
        status_atual["texto_rodada_atual"] = texto_rodada_atual
    
    return jsonify(status_atual)

@app.route('/api/iniciar', methods=['POST'])
def iniciar_jogo():
    # Verifica se há jogadores configurados
    if not partida["participantes"]:
        return jsonify({
            "erro": "Nenhum jogador configurado",
            "mensagem": "Configure os jogadores antes de iniciar o jogo",
            "status": "erro"
        }), 400
    
    # Verifica se o jogo está em estado válido para iniciar
    if partida["status"] not in ["aguardando", "apresentacao"]:
        return jsonify({
            "erro": "Estado inválido para iniciar o jogo",
            "status_atual": partida["status"]
        }), 400
    
    # Inicia o jogo
    partida["status"] = "iniciada"
    partida["rodada_atual"] = 0
    
    # Resetar pontuações
    for p in partida["participantes"]:
        p["pontuacao"] = 0
    
    return jsonify({
        "mensagem": "Jogo iniciado",
        "status": partida["status"],
        "jogadores": partida["participantes"]
    })

@app.route('/api/proxima_rodada', methods=['POST'])
def proxima_rodada():
    if partida["status"] in ["iniciada", "rodada_ativa"]:
        partida["rodada_atual"] += 1
        
        # Resetar timer quando uma nova rodada começa
        partida["timer_ativo"] = False
        partida["tempo_inicio"] = 0
        partida["duracao_rodada"] = 30.0  # Reset para o valor padrão
        
        # Obtém o total de rodadas da configuração
        total_rodadas = partida["configuracao"].get("total_rodadas", 10)
        
        if partida["rodada_atual"] > total_rodadas:
            partida["status"] = "finalizada"
            return jsonify({"mensagem": "Jogo finalizado", "status": partida["status"]})
        
        partida["status"] = "rodada_ativa"
        return jsonify({
            "mensagem": f"Rodada {partida['rodada_atual']} iniciada",
            "status": partida["status"],
            "rodada_atual": partida["rodada_atual"],
            "timer_resetado": True  # Informação adicional sobre o reset do timer
        })
    
    return jsonify({"erro": "Não é possível avançar para próxima rodada"})

@app.route('/api/pergunta_atual', methods=['GET'])
def pergunta_atual():
    # Obtém o total de rodadas da configuração
    total_rodadas = partida["configuracao"].get("total_rodadas", 10)
    
    # Melhorar a resposta informativa
    resposta = {
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": total_rodadas
    }
    
    # Determina se a rodada atual é a última
    rodada_atual_e_ultima = partida["rodada_atual"] == total_rodadas
    
    # Formata o texto da rodada atual
    texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else str(partida["rodada_atual"])
    resposta["texto_rodada_atual"] = texto_rodada_atual
    
    if partida["status"] != "rodada_ativa":
        resposta["erro"] = "Não há rodada ativa"
        resposta["mensagem"] = "É necessário iniciar o jogo e avançar para uma rodada antes de solicitar a pergunta"
        return jsonify(resposta)
    
    # Obtém os dados da rodada atual
    dados_rodada = partida.get("rodada_dados", {})
    if not dados_rodada:
        resposta["erro"] = "Dados da rodada não encontrados"
        resposta["mensagem"] = "Não foi possível obter os dados da pergunta atual"
        return jsonify(resposta)
    
    # Retorna a pergunta da rodada atual
    pergunta_segura = {
        "texto": dados_rodada.get("pergunta", ""),
        "tema": dados_rodada.get("tema", "Geral"),
        "respostas": dados_rodada.get("opcoes", [])
    }
    
    # Adicionar os dados da pergunta à resposta
    resposta.update(pergunta_segura)
    
    # Adicionar informações extras para depuração
    resposta["debug"] = {
        "perguntas_disponiveis": len(perguntas),
        "indice_atual": partida["rodada_atual"] - 1
    }
    
    return jsonify(resposta)

@app.route('/api/enviar_resposta', methods=['POST'])
def enviar_resposta():
    try:
        # Obtém os dados da requisição
        if request.is_json:
            dados = request.json
        else:
            dados = request.form.to_dict()
        
        # Log para debug
        app.logger.info(f"Dados de resposta recebidos: {dados}")
        
        # Verifica se o jogo está em uma rodada ativa
        if partida["status"] != "rodada_ativa":
            return jsonify({
                "erro": "Não há uma rodada ativa para receber respostas",
                "status_atual": partida["status"]
            }), 400
        
        # Obtém a posição do jogador (1, 2, 3) em vez do ID
        posicao = dados.get("jogador") or dados.get("posicao")
        if not posicao:
            return jsonify({
                "erro": "É necessário informar a posição do jogador (1, 2 ou 3)",
                "dados_recebidos": dados
            }), 400
        
        # Converte para inteiro
        try:
            posicao = int(posicao)
        except ValueError:
            return jsonify({
                "erro": f"Posição de jogador inválida: {posicao}",
                "status": "erro"
            }), 400
        
        # Verifica se a posição é válida
        if posicao < 1 or posicao > len(partida["participantes"]):
            return jsonify({
                "erro": f"Posição {posicao} inválida. Total de jogadores: {len(partida['participantes'])}",
                "status": "erro"
            }), 400
        
        # Obtém o jogador correspondente à posição (0-indexed na lista)
        jogador = partida["participantes"][posicao - 1]
        jogador_id = str(jogador["id"])
        
        # Verifica se o jogador já enviou uma resposta nesta rodada
        if jogador_id in partida.get("respostas_recebidas", set()):
            return jsonify({
                "erro": "Este jogador já enviou uma resposta para esta rodada",
                "jogador_id": jogador_id,
                "jogador_nome": jogador["nome"],
                "jogador_posicao": posicao
            }), 400
        
        # Registra que o jogador enviou uma resposta
        if "respostas_recebidas" not in partida:
            partida["respostas_recebidas"] = set()
        partida["respostas_recebidas"].add(jogador_id)
        
        # Obtém a resposta escolhida - aceita 'resposta', 'opcao' ou 'opcao_id'
        resposta = dados.get("resposta")
        if resposta is None:
            resposta = dados.get("opcao")
        if resposta is None:
            resposta = dados.get("opcao_id")
        
        if resposta is None:
            return jsonify({
                "erro": "É necessário informar a resposta escolhida",
                "dados_recebidos": dados
            }), 400
        
        # Mapeia respostas alfabéticas para numéricas (A=1, B=2, etc.)
        if isinstance(resposta, str) and resposta.upper() in ["A", "B", "C", "D"]:
            mapeamento = {"A": 1, "B": 2, "C": 3, "D": 4}
            resposta = mapeamento[resposta.upper()]
        
        # Converte para inteiro
        try:
            resposta = int(resposta)
        except ValueError:
            return jsonify({
                "erro": f"Resposta inválida: {resposta}",
                "status": "erro"
            }), 400
        
        # Obtém o tempo de resposta (opcional)
        tempo = 0.0
        try:
            tempo = float(dados.get("tempo", 0.0))
        except ValueError:
            tempo = 0.0
        
        # Tempo real do servidor
        tempo_atual = time.time()
        
        # Verifica se o jogador respondeu antes do timer começar
        if tempo_atual < partida["tempo_inicio"]:
            # Penaliza o jogador por responder antes do tempo
            app.logger.warning(f"Jogador {jogador_id} ({jogador['nome']}) respondeu antes do timer iniciar!")
            
            # Marca que o jogador foi penalizado nesta rodada
            if "antecipacoes" not in partida:
                partida["antecipacoes"] = {}
            partida["antecipacoes"][jogador_id] = True
            
            # Adiciona na lista de respostas mas com pontuação zero
            if "respostas" not in partida:
                partida["respostas"] = {}
            
            partida["respostas"][jogador_id] = {
                "resposta": resposta,
                "tempo": 0,
                "correta": False,  # Considerada incorreta independente da escolha
                "pontos": 0,
                "antecipou": True
            }
            
            return jsonify({
                "jogador_id": jogador_id,
                "jogador_nome": jogador["nome"],
                "jogador_posicao": posicao,
                "resposta": resposta,
                "correta": False,
                "pontos_obtidos": 0,
                "pontuacao_total": jogador["pontuacao"],
                "mensagem": "Resposta antecipada! Você respondeu antes do timer começar."
            })
        
        # Busca a resposta correta para a rodada atual
        dados_rodada = partida.get("rodada_dados", {})
        resposta_correta = dados_rodada.get("resposta_correta", 1)
        
        # Verifica se a resposta está correta
        correta = (resposta == resposta_correta)
        
        # Calcula os pontos com base na resposta e tempo
        pontos = 0
        tempo_max = partida["duracao_rodada"]
        
        if correta:
            # Pontuação base por acerto
            pontos_base = 10
            
            # Bônus por tempo (quanto mais rápido, mais pontos)
            if tempo > 0 and tempo_max > 0:
                fator_tempo = max(0, 1 - (tempo / (tempo_max * 1000)))
                bonus_tempo = int(10 * fator_tempo)
                pontos = pontos_base + bonus_tempo
            else:
                pontos = pontos_base
        
        # Armazena a resposta do jogador
        if "respostas" not in partida:
            partida["respostas"] = {}
        
        partida["respostas"][jogador_id] = {
            "resposta": resposta,
            "tempo": tempo,
            "correta": correta,
            "pontos": pontos,
            "antecipou": False
        }
        
        # Atualiza dados do jogador na sessão atual
        jogador["pontuacao"] += pontos
        
        # Verifica se todos os jogadores já responderam
        todos_responderam = len(partida.get("respostas_recebidas", set())) >= len(partida["participantes"])
        
        if todos_responderam:
            app.logger.info("Todos os jogadores responderam! Preparando para avançar para a próxima rodada.")
            
            # Agenda a finalização automática da rodada
            # Isto será implementado em um thread separado em uma implementação real
            # Por ora, apenas definimos uma flag
            partida["avancar_rodada"] = True
        
        # Retorna o resultado
        resultado = {
            "jogador_id": jogador_id,
            "jogador_nome": jogador["nome"],
            "jogador_posicao": posicao,
            "resposta": resposta,
            "correta": correta,
            "pontos_obtidos": pontos,
            "pontuacao_total": jogador["pontuacao"],
            "todos_responderam": todos_responderam
        }
        
        if todos_responderam:
            resultado["avancar_para"] = "próxima rodada"
        
        return jsonify(resultado)
    
    except Exception as e:
        app.logger.error(f"Erro ao processar resposta: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "erro": "Erro ao processar resposta",
            "detalhes": str(e),
            "status": "erro"
        }), 500

@app.route('/api/resultados', methods=['GET'])
def resultados():
    # Construir a classificação com base nas pontuações
    classificacao = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao"],
        reverse=True  # Ordem decrescente (maior pontuação primeiro)
    )
    
    return jsonify({
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "classificacao": classificacao
    })

# Endpoint para reiniciar o jogo após finalizado
@app.route('/api/reiniciar', methods=['POST'])
def reiniciar_jogo():
    # Reinicia o jogo, mas mantém os jogadores
    jogadores_atuais = partida["participantes"]
    
    # Reset do estado do jogo
    partida["status"] = "aguardando"
    partida["rodada_atual"] = 0
    partida["timer_ativo"] = False
    partida["tempo_inicio"] = 0
    
    # Mantém os mesmos jogadores, mas zera as pontuações
    for jogador in jogadores_atuais:
        jogador["pontuacao"] = 0
    
    partida["participantes"] = jogadores_atuais
    
    return jsonify({
        "mensagem": "Jogo reiniciado e pronto para uma nova partida",
        "status": partida["status"],
        "participantes": partida["participantes"]
    })

# Endpoint para modo de espera/apresentação
@app.route('/api/modo_apresentacao', methods=['POST'])
def modo_apresentacao():
    # Aceita parâmetros para personalização do modo apresentação
    dados = request.json if request.is_json else {}
    
    # Configura o estado de apresentação
    partida["status"] = "apresentacao"
    partida["rodada_atual"] = 0
    partida["timer_ativo"] = False
    
    # Zera explicitamente o valor de próxima rodada e remove texto_proxima_rodada
    partida["proxima_rodada"] = 0
    if "texto_proxima_rodada" in partida:
        del partida["texto_proxima_rodada"]
    
    # Inicializa o histórico se não existir
    if "historico" not in partida:
        partida["historico"] = {
            "total_partidas": 0,
            "recorde_pontos": 0,
            "recordista": None
        }
    
    # Opcionalmente recebe mensagem personalizada
    mensagem = dados.get("mensagem", "Quiz Game - Aguardando início da partida")
    tema = dados.get("tema", "default")
    
    # Ranking global (ordenado por pontuação total)
    ranking_global = sorted(
        jogadores_cadastrados["jogadores"],  # Usando os jogadores cadastrados ao invés dos participantes
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    # Certifica-se que a última partida existe
    if "ultima_partida" not in partida:
        partida["ultima_partida"] = {
            "data": None,
            "vencedor": None,
            "pontuacao_maxima": 0
        }
    
    # Retorna a estrutura exata necessária
    return jsonify({
        # Estado do Jogo
        "status": partida["status"],
        "mensagem": mensagem,
        "tema": tema,
        "ultima_atualizacao": time.time(),
        
        # Ranking Global
        "jogador1_pontos": ranking_global[0]["pontuacao_total"] if len(ranking_global) > 0 else 0,
        "jogador2_pontos": ranking_global[1]["pontuacao_total"] if len(ranking_global) > 1 else 0,
        "jogador3_pontos": ranking_global[2]["pontuacao_total"] if len(ranking_global) > 2 else 0,
        "jogador1_nome": ranking_global[0]["nome"] if len(ranking_global) > 0 else "Jogador 1",
        "jogador2_nome": ranking_global[1]["nome"] if len(ranking_global) > 1 else "Jogador 2",
        "jogador3_nome": ranking_global[2]["nome"] if len(ranking_global) > 2 else "Jogador 3",
        "jogador1_foto": ranking_global[0]["foto"] if len(ranking_global) > 0 else "https://randomuser.me/api/portraits/lego/1.jpg",
        "jogador2_foto": ranking_global[1]["foto"] if len(ranking_global) > 1 else "https://randomuser.me/api/portraits/lego/2.jpg",
        "jogador3_foto": ranking_global[2]["foto"] if len(ranking_global) > 2 else "https://randomuser.me/api/portraits/lego/3.jpg",
        
        # Rodadas
        "total_rodadas": partida["total_rodadas"],
        "duracao_rodada": partida["duracao_rodada"],
        "total_partidas": partida["historico"]["total_partidas"],
        "ultima_partida_data": partida["ultima_partida"]["data"] if partida["ultima_partida"]["data"] else time.time()
    })

# Endpoint para obter o status do modo apresentação
@app.route('/api/status_apresentacao', methods=['GET'])
def status_apresentacao():
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "O jogo não está em modo apresentação",
            "status_atual": partida["status"]
        })
    
    # Obtém a classificação dos jogadores para exibir no modo espera
    classificacao = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao"],
        reverse=True
    )
    
    # Ranking global (ordenado por pontuação total)
    ranking_global = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    # Informações adicionais para exibição
    total_jogos_anteriores = 0  # Idealmente seria armazenado em um banco de dados
    ultima_atualizacao = time.time()
    
    return jsonify({
        "status": "apresentacao",
        "mensagem": partida.get("mensagem_apresentacao", "Quiz Game - Aguardando início da partida"),
        "tema": partida.get("tema_apresentacao", "default"),
        "classificacao": classificacao,
        "ranking_global": ranking_global,
        "total_jogos_anteriores": total_jogos_anteriores,
        "jogadores_conectados": len(partida["participantes"]),
        "timestamp": ultima_atualizacao
    })

# Endpoint para listar temas disponíveis
@app.route('/api/temas', methods=['GET'])
def listar_temas():
    # Extrai os temas únicos das perguntas
    temas = set(p["tema"] for p in todas_perguntas)
    
    return jsonify({
        "temas": list(temas)
    })

# Endpoints para controle do timer
@app.route('/api/iniciar_timer', methods=['POST'])
def iniciar_timer():
    # Aceita tanto JSON quanto query parameters
    try:
        # Tenta obter dados do JSON
        if request.is_json:
            data = request.json
        else:
            # Fallback para form data ou query parameters
            data = request.form.to_dict() if request.form else {}
        
        # Se não tem dados no corpo, tenta obter dos query parameters
        duracao = data.get('duracao')
        if duracao is None:
            duracao = request.args.get('duracao', 30.0)
            
        # Converte para float
        duracao = float(duracao)
        
        print(f"Iniciando timer com duração: {duracao}")
    except Exception as e:
        # Em caso de erro, usa valor padrão e loga o erro
        duracao = 30.0
        print(f"Erro ao processar duração do timer: {e}, usando valor padrão: {duracao}")
    
    if partida["status"] != "rodada_ativa":
        return jsonify({"erro": "Não há rodada ativa para iniciar o timer"}), 400
    
    # Inicia o timer
    partida["timer_ativo"] = True
    partida["tempo_inicio"] = time.time()
    partida["duracao_rodada"] = duracao
    
    return jsonify({
        "mensagem": "Timer iniciado",
        "duracao": duracao,
        "tempo_inicio": partida["tempo_inicio"],
        "rodada_atual": partida["rodada_atual"]
    })

@app.route('/api/tempo_restante', methods=['GET'])
def tempo_restante():
    # Se o timer não está ativo, retorna erro
    if not partida["timer_ativo"]:
        return jsonify({
            "erro": "Timer não está ativo",
            "status": partida["status"],
            "rodada_atual": partida["rodada_atual"],
            "timer_ativo": False
        })
    
    # Calcula tempo restante
    tempo_decorrido = time.time() - partida["tempo_inicio"]
    tempo_rest = max(0, partida["duracao_rodada"] - tempo_decorrido)
    
    # Se o tempo acabou, desativa o timer
    if tempo_rest <= 0:
        partida["timer_ativo"] = False
        tempo_rest = 0
    
    return jsonify({
        "tempo_restante": tempo_rest,
        "duracao_total": partida["duracao_rodada"],
        "rodada_atual": partida["rodada_atual"],
        "status": partida["status"],
        "timer_ativo": partida["timer_ativo"]
    })

@app.route('/api/cancelar_timer', methods=['POST'])
def cancelar_timer():
    # Também aceita qualquer formato de requisição
    if not partida["timer_ativo"]:
        return jsonify({"mensagem": "Timer já está inativo"})
    
    partida["timer_ativo"] = False
    
    return jsonify({
        "mensagem": "Timer cancelado",
        "rodada_atual": partida["rodada_atual"],
        "status": partida["status"]
    })

# Endpoint para verificar se uma partida foi concluída
@app.route('/api/verificar_fim_jogo', methods=['GET'])
def verificar_fim_jogo():
    # Verifica se todas as rodadas foram concluídas
    jogo_finalizado = partida["rodada_atual"] >= partida["total_rodadas"]
    
    # Se o jogo já está marcado como finalizado, retorna essa informação
    if partida["status"] == "finalizado":
        jogo_finalizado = True
    
    # Se detectou que o jogo acabou, atualiza o status
    if jogo_finalizado and partida["status"] != "finalizado":
        partida["status"] = "finalizado"
    
    # Retorna o vencedor se o jogo estiver finalizado
    vencedor = None
    if jogo_finalizado:
        classificacao = sorted(
            partida["participantes"],
            key=lambda x: x["pontuacao"],
            reverse=True
        )
        if classificacao:
            vencedor = classificacao[0]
    
    return jsonify({
        "jogo_finalizado": jogo_finalizado,
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "vencedor": vencedor
    })

# Endpoint para configurar os jogadores antes de iniciar a partida
@app.route('/api/configurar_jogadores', methods=['POST'])
def configurar_jogadores():
    # Verifica se o jogo está em modo apresentação ou aguardando
    if partida["status"] not in ["apresentacao", "aguardando"]:
        return jsonify({
            "erro": "Não é possível configurar jogadores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Obtém os dados dos jogadores
    dados = request.json if request.is_json else {}
    jogadores = dados.get("jogadores", [])
    
    # Validação básica
    if not jogadores:
        return jsonify({
            "erro": "Nenhum jogador fornecido",
            "status": "erro"
        }), 400
    
    # Validação dos dados de cada jogador
    jogadores_validos = []
    ids_utilizados = set()  # Conjunto para verificar IDs duplicados
    
    for jogador in jogadores:
        # Verifica campos obrigatórios
        if not all(k in jogador for k in ["id", "nome"]):
            return jsonify({
                "erro": "Dados incompletos do jogador",
                "jogador": jogador,
                "status": "erro"
            }), 400
        
        # Verifica se o ID é único na configuração atual
        if jogador["id"] in ids_utilizados:
            return jsonify({
                "erro": "ID duplicado",
                "jogador": jogador,
                "status": "erro"
            }), 400
        
        # Verifica se o jogador existe no cadastro
        jogador_cadastrado = None
        for j in jogadores_cadastrados["jogadores"]:
            if j["id"] == jogador["id"]:
                jogador_cadastrado = j
                break
        
        if not jogador_cadastrado:
            return jsonify({
                "erro": "Jogador não encontrado no cadastro",
                "jogador": jogador,
                "status": "erro"
            }), 404
        
        # Adiciona o ID ao conjunto de IDs utilizados
        ids_utilizados.add(jogador["id"])
        
        # Cria o jogador validado com dados do cadastro
        jogador_validado = {
            "id": jogador_cadastrado["id"],
            "nome": jogador_cadastrado["nome"],
            "foto": jogador_cadastrado["foto"],
            "telefone": jogador_cadastrado["telefone"],
            "pontuacao": 0,  # Pontuação da partida atual
            "pontuacao_total": jogador_cadastrado["pontuacao_total"],
            "partidas_jogadas": jogador_cadastrado["partidas_jogadas"],
            "vitorias": jogador_cadastrado["vitorias"]
        }
        jogadores_validos.append(jogador_validado)
    
    # Atualiza os participantes da partida
    partida["participantes"] = jogadores_validos
    
    # Atualiza o status para aguardando início
    partida["status"] = "aguardando"
    
    return jsonify({
        "mensagem": "Jogadores configurados com sucesso",
        "status": partida["status"],
        "jogadores": jogadores_validos,
        "total_jogadores": len(jogadores_validos)
    })

# Endpoint para entrar no modo de seleção
@app.route('/api/modo_selecao', methods=['POST'])
def modo_selecao():
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível entrar no modo seleção neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Configura o estado de seleção
    partida["status"] = "selecao"
    partida["configuracao"]["status"] = "pendente"
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "status": "selecao",
        "mensagem": "Modo seleção ativado",
        "jogadores_disponiveis": jogadores_disponiveis,
        "configuracao_atual": partida["configuracao"]
    })

# Endpoint para configurar os parâmetros da partida
@app.route('/api/configurar_partida', methods=['POST'])
def configurar_partida():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "Não é possível configurar a partida neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Obtém os dados da configuração
    dados = request.json if request.is_json else request.form.to_dict()
    
    # Verificar se estamos recebendo parâmetros individuais para jogadores ou o array
    jogador1 = dados.get("jogador1")
    jogador2 = dados.get("jogador2")
    jogador3 = dados.get("jogador3")
    
    # Se tiver parâmetros individuais, converte para array
    if jogador1 is not None and jogador2 is not None and jogador3 is not None:
        jogadores_selecionados = [int(jogador1), int(jogador2), int(jogador3)]
    else:
        # Tenta obter o array de jogadores
        jogadores = dados.get("jogadores")
        
        # Se jogadores for uma string no formato "[1,2,4]", converte para lista
        if isinstance(jogadores, str):
            try:
                # Tenta converter de string JSON para lista
                if jogadores.startswith('[') and jogadores.endswith(']'):
                    import json
                    jogadores_selecionados = json.loads(jogadores)
                # Alternativamente, tenta separar por vírgulas
                else:
                    jogadores_selecionados = [int(j.strip()) for j in jogadores.split(',') if j.strip().isdigit()]
            except Exception as e:
                app.logger.error(f"Erro ao processar jogadores: {e}")
                jogadores_selecionados = []
        else:
            jogadores_selecionados = jogadores if isinstance(jogadores, list) else []
    
    # Duração da rodada (segundos)
    try:
        duracao_rodada = float(dados.get("duracao_rodada", 30.0))
    except (ValueError, TypeError):
        duracao_rodada = 30.0
    
    # Total de rodadas
    try:
        total_rodadas = int(dados.get("total_rodadas", 10))
    except (ValueError, TypeError):
        total_rodadas = 10
    
    # Tema visual
    tema = dados.get("tema", "default")
    
    # Log para debug
    app.logger.info(f"Dados recebidos: {dados}")
    app.logger.info(f"Jogadores selecionados: {jogadores_selecionados}")
    
    # Validação dos jogadores selecionados
    if len(jogadores_selecionados) != 3:
        return jsonify({
            "erro": "É necessário selecionar exatamente 3 jogadores",
            "status": "erro",
            "recebido": jogadores_selecionados
        }), 400
    
    # Validação dos jogadores existentes
    for jogador_id in jogadores_selecionados:
        if not any(j["id"] == jogador_id for j in jogadores_cadastrados["jogadores"]):
            return jsonify({
                "erro": f"Jogador com ID {jogador_id} não encontrado",
                "status": "erro"
            }), 400
    
    # Validação dos parâmetros da partida
    if duracao_rodada <= 0:
        return jsonify({
            "erro": "A duração da rodada deve ser um valor positivo",
            "status": "erro"
        }), 400
    
    if total_rodadas <= 0:
        return jsonify({
            "erro": "O total de rodadas deve ser um valor positivo",
            "status": "erro"
        }), 400
    
    # Atualiza a configuração
    partida["configuracao"]["jogadores_selecionados"] = jogadores_selecionados
    partida["configuracao"]["duracao_rodada"] = duracao_rodada
    partida["configuracao"]["total_rodadas"] = total_rodadas
    partida["configuracao"]["tema"] = tema
    partida["configuracao"]["status"] = "validada"
    
    # Atualiza os parâmetros gerais da partida
    partida["duracao_rodada"] = duracao_rodada
    partida["total_rodadas"] = total_rodadas
    
    return jsonify({
        "mensagem": "Configuração da partida atualizada com sucesso",
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter o status da configuração
@app.route('/api/status_selecao', methods=['GET'])
def status_selecao():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "O jogo não está em modo seleção",
            "status_atual": partida["status"]
        })
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "status": "selecao",
        "configuracao": partida["configuracao"],
        "jogadores_disponiveis": jogadores_disponiveis,
        "jogadores_selecionados": [
            next((j for j in jogadores_disponiveis if j["id"] == id), None)
            for id in partida["configuracao"]["jogadores_selecionados"]
        ]
    })

# Endpoint para iniciar a partida
@app.route('/api/iniciar_partida', methods=['POST'])
def iniciar_partida():
    # Verifica se o jogo está em modo seleção ou aguardando
    if partida["status"] not in ["selecao", "aguardando"]:
        return jsonify({
            "erro": "Não é possível iniciar a partida neste momento",
            "status": partida["status"]
        }), 400
    
    # Verifica se há jogadores selecionados
    if not partida["configuracao"]["jogadores_selecionados"]:
        return jsonify({
            "erro": "Selecione pelo menos um jogador para iniciar a partida",
            "status": "erro"
        }), 400
    
    # Limpa lista de participantes anterior e configura novos participantes
    partida["participantes"] = []
    
    # Configura os participantes de acordo com jogadores selecionados
    for jogador_id in partida["configuracao"]["jogadores_selecionados"]:
        # Encontra os detalhes do jogador pelo ID
        jogador = None
        for j in jogadores_cadastrados["jogadores"]:
            if j["id"] == jogador_id:
                jogador = j
                break
        
        if jogador:
            # Cria uma cópia do jogador para não modificar o original
            participante = jogador.copy()
            # Adiciona a pontuação zerada para a partida
            participante["pontuacao"] = 0
            # Adiciona à lista de participantes
            partida["participantes"].append(participante)
    
    # Verifica se os participantes foram configurados corretamente
    if not partida["participantes"]:
        return jsonify({"erro": "Falha ao configurar participantes"}), 500
    
    # Atualiza o status da partida
    partida["status"] = "iniciada"
    partida["rodada_atual"] = 0  # Rodada inicial zerada
    partida["proxima_rodada"] = 0  # Também zera proxima_rodada
    partida["ultima_atualizacao"] = time.time()
    
    # Texto da rodada atual deve ser sempre "1" ao iniciar uma partida
    texto_rodada_atual = "1"
    
    # Retorna o status atualizado
    return jsonify({
        "mensagem": "Partida iniciada com sucesso",
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "texto_rodada_atual": texto_rodada_atual,
        "total_rodadas": partida["total_rodadas"],
        "participantes": partida["participantes"]
    })

# Endpoint para resetar o jogo
@app.route('/api/reset', methods=['POST'])
def reset():
    # Reseta a partida para o estado inicial
    global partida
    global configuracao_padrao
    
    partida = {
        "status": "apresentacao",
        "configuracao": {
            "status": "pendente",
            "duracao_rodada": 30,
            "total_rodadas": 10,
            "jogadores_selecionados": []
        },
        "participantes": [],
        "rodada_atual": 0,
        "proxima_rodada": 0,  # Zera a próxima rodada explicitamente
        "timer_ativo": False,
        "ultima_atualizacao": time.time()
    }
    
    # Reseta a lista de perguntas aleatórias selecionadas
    selecionar_perguntas_aleatorias()
    
    # Retorna o novo estado
    return jsonify({
        "mensagem": "Partida resetada com sucesso",
        "status": "apresentacao"
    })

@app.route('/api/nova_partida', methods=['POST'])
def nova_partida():
    # Reseta a partida para o estado inicial
    global partida
    global perguntas
    
    # Log para registro
    app.logger.info("Criando nova partida")
    
    # Inicializa a configuração básica
    partida["status"] = "apresentacao"
    partida["rodada_atual"] = 0
    partida["proxima_rodada"] = 0  # Explicitamente zerado
    if "texto_proxima_rodada" in partida:
        del partida["texto_proxima_rodada"]  # Remove caso exista
    partida["timer_ativo"] = False
    partida["tempo_inicio"] = 0
    partida["ultima_atualizacao"] = time.time()
    
    # Limpa dados específicos de rodadas
    if "respostas" in partida:
        del partida["respostas"]
    if "respostas_recebidas" in partida:
        del partida["respostas_recebidas"]
    if "avancar_rodada" in partida:
        del partida["avancar_rodada"]
    if "antecipacoes" in partida:
        del partida["antecipacoes"]
    
    # Reseta a configuração
    partida["configuracao"] = {
        "jogadores_selecionados": [],
        "duracao_rodada": 30.0,
        "total_rodadas": 10,
        "tema": "default",
        "status": "pendente"
    }
    
    # Atualiza o total de rodadas no objeto da partida
    partida["total_rodadas"] = partida["configuracao"]["total_rodadas"]
    partida["duracao_rodada"] = partida["configuracao"]["duracao_rodada"]
    
    # Seleciona perguntas aleatórias
    try:
        perguntas = selecionar_perguntas_aleatorias()
        app.logger.info(f"Selecionadas {len(perguntas)} perguntas aleatórias para a partida")
    except Exception as e:
        app.logger.error(f"Erro ao selecionar perguntas: {str(e)}")
    
    # Retorna o estado atual do jogo com jogadores disponíveis
    return jsonify({
        "status": partida["status"],
        "mensagem": "Nova partida criada",
        "jogadores_disponíveis": jogadores_cadastrados["jogadores"]
    })

# Endpoint para iniciar uma nova rodada
@app.route('/api/iniciar_rodada', methods=['POST'])
def iniciar_rodada():
    # Permite acesso às variáveis globais
    global perguntas
    
    # Verifica se o jogo está iniciado ou em modo abertura
    if partida["status"] not in ["iniciada", "abertura"]:
        return jsonify({
            "erro": "Não é possível iniciar uma rodada neste momento",
            "status": partida["status"]
        }), 400
    
    # Incrementa o contador de rodada se estamos em abertura
    if partida["status"] == "abertura":
        partida["rodada_atual"] = partida["proxima_rodada"]
    
    # Atualiza o status da partida
    partida["status"] = "rodada_ativa"
    
    # Prepara estrutura para respostas
    partida["respostas"] = {}
    
    # Registra as respostas recebidas por jogador
    partida["respostas_recebidas"] = set()
    
    # Obtém a pergunta da rodada atual a partir da lista de perguntas selecionadas
    indice_pergunta = partida["rodada_atual"] - 1
    
    # Verifica se perguntas existe e não é None
    if perguntas is None:
        app.logger.error("Lista de perguntas é None. Tentando selecionar novamente.")
        try:
            # Tenta selecionar perguntas novamente
            perguntas = selecionar_perguntas_aleatorias()
            app.logger.info(f"Re-selecionadas {len(perguntas)} perguntas para a partida")
        except Exception as e:
            app.logger.error(f"Erro ao re-selecionar perguntas: {str(e)}")
            return jsonify({
                "erro": "Falha ao carregar perguntas para o quiz",
                "status": partida["status"]
            }), 500
    
    # Verifica se temos perguntas suficientes
    if not perguntas or 0 > indice_pergunta or indice_pergunta >= len(perguntas):
        return jsonify({
            "erro": f"Índice de pergunta inválido: {indice_pergunta}. Total de perguntas: {len(perguntas) if perguntas else 0}",
            "status": partida["status"]
        }), 400
    
    pergunta_atual = perguntas[indice_pergunta]
    # Converte a resposta correta se estiver em formato alfabético (A, B, C)
    resposta_correta = pergunta_atual["resposta_correta"]
    if isinstance(resposta_correta, str) and resposta_correta.upper() in ["A", "B", "C", "D"]:
        mapeamento = {"A": 1, "B": 2, "C": 3, "D": 4}
        resposta_correta_num = mapeamento.get(resposta_correta.upper(), 0)
    else:
        resposta_correta_num = resposta_correta
    
    # Guarda a resposta correta para futura validação
    partida["resposta_correta"] = resposta_correta_num
    
    # Atualiza o momento de início da rodada
    partida["tempo_inicio"] = time.time()
    partida["ultima_atualizacao"] = time.time()
    
    # Ativa o timer
    partida["timer_ativo"] = True
    
    # Prepara respostas para formatação na interface
    opcoes = []
    for opcao in pergunta_atual["respostas"]:
        opcoes.append({
            "id": mapeamento.get(opcao["opcao"].upper(), 0),
            "texto": opcao["texto"]
        })
    
    # Formata texto da rodada atual como número ou "FINAL"
    if partida["rodada_atual"] == partida["total_rodadas"]:
        texto_rodada_atual = "FINAL"
    else:
        texto_rodada_atual = str(partida["rodada_atual"])
    
    # Log
    app.logger.info(f"Iniciando rodada {texto_rodada_atual}")
    
    # Retorna os dados da pergunta
    return jsonify({
        "rodada_atual": partida["rodada_atual"],
        "texto_rodada_atual": texto_rodada_atual,
        "tema": pergunta_atual.get("tema", "Geral"),
        "pergunta": pergunta_atual["texto"],
        "alternativas": opcoes,
        "duracao_rodada": partida["duracao_rodada"],
        "total_rodadas": partida["total_rodadas"]
    })

# Endpoint para finalizar a rodada atual
@app.route('/api/finalizar_rodada', methods=['POST'])
def finalizar_rodada():
    # Obtém o total de rodadas da configuração
    total_rodadas = partida["configuracao"].get("total_rodadas", 10)
    
    # Verifica se o jogo está em uma rodada ativa
    if partida["status"] != "rodada_ativa":
        # Determina se a rodada atual é a última
        rodada_atual_e_ultima = partida["rodada_atual"] == total_rodadas
        
        # Formata o texto da rodada atual
        texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else (
            "1" if partida["rodada_atual"] == 0 else str(partida["rodada_atual"])
        )
        
        return jsonify({
            "erro": "Não há uma rodada ativa para finalizar",
            "status_atual": partida["status"],
            "rodada_atual": partida["rodada_atual"],
            "texto_rodada_atual": texto_rodada_atual
        }), 400
    
    try:
        # Log para debug
        app.logger.info("Finalizando rodada usando dados de respostas do servidor")
        
        # Monta o objeto de pontos a partir das respostas já registradas no servidor
        pontos = {}
        for jogador_id, resposta_info in partida.get("respostas", {}).items():
            pontos[jogador_id] = resposta_info["pontos"]
        
        # Para jogadores que não responderam, atribui 0 pontos
        for jogador in partida["participantes"]:
            jogador_id = str(jogador["id"])
            if jogador_id not in pontos:
                pontos[jogador_id] = 0
        
        app.logger.info(f"Pontos calculados a partir das respostas: {pontos}")
        
        # Atualiza a pontuação dos participantes
        for jogador in partida["participantes"]:
            jogador_id = str(jogador["id"])
            if jogador_id in pontos:
                jogador["pontuacao"] += pontos[jogador_id]
                jogador["pontuacao_total"] += pontos[jogador_id]
        
        # Salva o número da rodada atual antes de continuar
        rodada_atual_finalizada = partida["rodada_atual"]
        
        # Verifica se é a última rodada
        if partida["rodada_atual"] >= total_rodadas:
            # Determina o vencedor
            vencedor = max(partida["participantes"], key=lambda x: x["pontuacao"])
            vencedor["vitorias"] += 1
            
            # Atualiza o histórico
            partida["ultima_partida"] = {
                "data": time.time(),
                "vencedor": {
                    "id": vencedor["id"],
                    "nome": vencedor["nome"],
                    "foto": vencedor["foto"],
                    "pontuacao": vencedor["pontuacao"]
                },
                "pontuacao_maxima": vencedor["pontuacao"]
            }
            
            # Finaliza a partida
            partida["status"] = "finalizada"
            
            return jsonify({
                "mensagem": f"Rodada {rodada_atual_finalizada} finalizada",
                "status": "finalizada",
                "participantes": partida["participantes"],
                "ultima_partida": partida["ultima_partida"],
                "pontuacoes": pontos,
                "rodada_atual": partida["rodada_atual"],
                "texto_rodada_atual": "FINAL"
            })
        
        # NOVO CÓDIGO: Incrementa automaticamente a rodada
        partida["rodada_atual"] += 1
        
        # Determina se a próxima rodada é a última
        rodada_atual_e_ultima = partida["rodada_atual"] == total_rodadas
        
        # Formata o texto da rodada atual (agora já incrementada)
        texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else str(partida["rodada_atual"])
        
        # NOVO CÓDIGO: Atualiza as informações de abertura da rodada (mesmo que o endpoint /api/abertura_rodada faz)
        partida["proxima_rodada"] = partida["rodada_atual"]
        partida["status"] = "abertura"
        partida["tempo_abertura"] = 15  # Tempo de abertura em segundos
        partida["tempo_inicio"] = time.time()
        partida["ultima_atualizacao"] = time.time()
        
        # Limpa as respostas da rodada anterior
        if "respostas" in partida:
            partida["respostas"] = {}
        
        # Limpa a contagem de antecipações
        partida["antecipacoes"] = {}
        
        # Registra as respostas recebidas por jogador
        partida["respostas_recebidas"] = set()
        
        app.logger.info(f"Rodada {rodada_atual_finalizada} finalizada. Preparando abertura da rodada {texto_rodada_atual}.")
        
        return jsonify({
            "mensagem": f"Rodada {rodada_atual_finalizada} finalizada. Preparando abertura da rodada {texto_rodada_atual}.",
            "rodada_finalizada": rodada_atual_finalizada,
            "rodada_atual": partida["rodada_atual"],
            "texto_rodada_atual": texto_rodada_atual,
            "status": partida["status"],
            "participantes": partida["participantes"],
            "pontuacoes": pontos,
            "tempo_abertura": partida["tempo_abertura"],
            "inicio_timer": partida["tempo_inicio"]
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao finalizar/iniciar rodada: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "erro": "Erro ao processar requisição",
            "detalhes": str(e),
            "status": "erro",
            "rodada_atual": partida.get("rodada_atual", 0),
            "texto_rodada_atual": "Erro"
        }), 500

# Endpoint para aguardar
@app.route('/api/aguardar', methods=['POST'])
def aguardar():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "Não é possível aguardar neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Verifica se a configuração está validada
    if partida["configuracao"]["status"] != "validada":
        return jsonify({
            "erro": "A configuração da partida não está validada",
            "status": "erro"
        }), 400
    
    # Configura o estado de aguardando
    partida["status"] = "aguardando"
    partida["ultima_atualizacao"] = time.time()
    
    return jsonify({
        "mensagem": "Jogo em modo aguardando",
        "status": "aguardando",
        "configuracao": partida["configuracao"]
    })

# Endpoint para cadastrar um novo jogador
@app.route('/api/cadastrar_jogador', methods=['POST'])
def cadastrar_jogador():
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível cadastrar jogadores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Obtém os dados do jogador
    dados = request.json if request.is_json else {}
    
    # Validação dos dados
    if not dados.get("nome"):
        return jsonify({
            "erro": "O nome do jogador é obrigatório",
            "status": "erro"
        }), 400
    
    # Gera um ID único para o jogador
    novo_id = max([j["id"] for j in jogadores_cadastrados["jogadores"]], default=0) + 1
    
    # Cria o novo jogador
    novo_jogador = {
        "id": novo_id,
        "nome": dados["nome"],
        "foto": dados.get("foto", f"https://randomuser.me/api/portraits/lego/{novo_id}.jpg"),
        "pontuacao_total": 0,
        "partidas_jogadas": 0,
        "vitorias": 0
    }
    
    # Adiciona o jogador à lista de cadastrados
    jogadores_cadastrados["jogadores"].append(novo_jogador)
    
    return jsonify({
        "mensagem": "Jogador cadastrado com sucesso",
        "jogador": novo_jogador
    })

# Endpoint para listar todos os jogadores cadastrados
@app.route('/api/jogadores', methods=['GET'])
def listar_jogadores():
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível listar jogadores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Lista todos os jogadores cadastrados
    jogadores = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "jogadores": jogadores,
        "total": len(jogadores)
    })

# Endpoint para remover um jogador
@app.route('/api/remover_jogador/<int:jogador_id>', methods=['DELETE'])
def remover_jogador(jogador_id):
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível remover jogadores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Verifica se o jogador existe
    jogador = next((j for j in jogadores_cadastrados["jogadores"] if j["id"] == jogador_id), None)
    if not jogador:
        return jsonify({
            "erro": "Jogador não encontrado",
            "status": "erro"
        }), 404
    
    # Remove o jogador da lista de cadastrados
    jogadores_cadastrados["jogadores"].remove(jogador)
    
    return jsonify({
        "mensagem": "Jogador removido com sucesso",
        "jogador": jogador
    })

# Endpoint para atualizar um jogador
@app.route('/api/atualizar_jogador/<int:jogador_id>', methods=['PUT'])
def atualizar_jogador(jogador_id):
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível atualizar jogadores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Verifica se o jogador existe
    jogador = next((j for j in jogadores_cadastrados["jogadores"] if j["id"] == jogador_id), None)
    if not jogador:
        return jsonify({
            "erro": "Jogador não encontrado",
            "status": "erro"
        }), 404
    
    # Obtém os dados do jogador
    dados = request.json if request.is_json else {}
    
    # Atualiza os dados do jogador
    if "nome" in dados:
        jogador["nome"] = dados["nome"]
    if "foto" in dados:
        jogador["foto"] = dados["foto"]
    
    return jsonify({
        "mensagem": "Jogador atualizado com sucesso",
        "jogador": jogador
    })

# Endpoint para obter um jogador específico
@app.route('/api/jogador/<int:jogador_id>', methods=['GET'])
def obter_jogador(jogador_id):
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível obter jogadores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Verifica se o jogador existe
    jogador = next((j for j in jogadores_cadastrados["jogadores"] if j["id"] == jogador_id), None)
    if not jogador:
        return jsonify({
            "erro": "Jogador não encontrado",
            "status": "erro"
        }), 404
    
    return jsonify({
        "jogador": jogador
    })

# Endpoint para obter a configuração atual
@app.route('/api/configuracao', methods=['GET'])
def obter_configuracao():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "Não é possível obter a configuração neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "configuracao": partida["configuracao"],
        "jogadores_disponiveis": jogadores_disponiveis,
        "jogadores_selecionados": [
            next((j for j in jogadores_disponiveis if j["id"] == id), None)
            for id in partida["configuracao"]["jogadores_selecionados"]
        ]
    })

# Endpoint para obter os participantes da partida
@app.route('/api/participantes', methods=['GET'])
def obter_participantes():
    # Verifica se o jogo está em modo aguardando ou iniciado
    if partida["status"] not in ["aguardando", "iniciada", "rodada_ativa", "finalizada"]:
        return jsonify({
            "erro": "Não é possível obter os participantes neste momento",
            "status_atual": partida["status"]
        }), 400
    
    return jsonify({
        "participantes": partida["participantes"],
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter o ranking dos jogadores
@app.route('/api/ranking', methods=['GET'])
def obter_ranking():
    # Verifica se o jogo está em modo aguardando ou iniciado
    if partida["status"] not in ["aguardando", "iniciada", "rodada_ativa", "finalizada"]:
        return jsonify({
            "erro": "Não é possível obter o ranking neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Ordena os participantes por pontuação
    ranking = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao"],
        reverse=True
    )
    
    return jsonify({
        "ranking": ranking,
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter o status do timer
@app.route('/api/timer', methods=['GET'])
def obter_timer():
    # Verifica se o jogo está em modo rodada ativa
    if partida["status"] != "rodada_ativa":
        return jsonify({
            "erro": "Não é possível obter o timer neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Calcula o tempo restante
    tempo_restante = max(0, partida["duracao_rodada"] - (time.time() - partida["tempo_inicio"]))
    
    return jsonify({
        "timer_ativo": partida["timer_ativo"],
        "tempo_restante": tempo_restante,
        "duracao_rodada": partida["duracao_rodada"],
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter o status da rodada atual
@app.route('/api/rodada', methods=['GET'])
def obter_rodada():
    # Verifica se o jogo está em modo rodada ativa
    if partida["status"] != "rodada_ativa":
        return jsonify({
            "erro": "Não é possível obter a rodada neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Calcula o tempo restante
    tempo_restante = max(0, partida["duracao_rodada"] - (time.time() - partida["tempo_inicio"]))
    
    return jsonify({
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "timer_ativo": partida["timer_ativo"],
        "tempo_restante": tempo_restante,
        "duracao_rodada": partida["duracao_rodada"],
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter o status da partida
@app.route('/api/partida', methods=['GET'])
def obter_partida():
    # Verifica se o jogo está em modo aguardando ou iniciado
    if partida["status"] not in ["aguardando", "iniciada", "rodada_ativa", "finalizada"]:
        return jsonify({
            "erro": "Não é possível obter a partida neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Calcula o tempo restante se estiver em uma rodada
    tempo_restante = max(0, partida["duracao_rodada"] - (time.time() - partida["tempo_inicio"])) if partida["timer_ativo"] else 0
    
    # Determina se a rodada atual é a última
    rodada_atual_e_ultima = partida["rodada_atual"] == partida["total_rodadas"]
    
    # Formata o texto da rodada atual
    # Se a rodada for 0 (partida iniciada mas sem nenhuma rodada ativa), exibir como 1
    texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else (
        "1" if partida["rodada_atual"] == 0 else str(partida["rodada_atual"])
    )
    
    return jsonify({
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "texto_rodada_atual": texto_rodada_atual,
        "total_rodadas": partida["total_rodadas"],
        "timer_ativo": partida["timer_ativo"],
        "tempo_restante": tempo_restante,
        "duracao_rodada": partida["duracao_rodada"],
        "ultima_atualizacao": partida["ultima_atualizacao"],
        "configuracao": partida["configuracao"],
        "participantes": partida["participantes"],
        "ultima_partida": partida["ultima_partida"] if partida["status"] == "finalizada" else None
    })

# Endpoint para obter os jogadores cadastrados
@app.route('/api/jogadores_cadastrados', methods=['GET'])
def obter_jogadores_cadastrados():
    # Verifica se o jogo está em modo apresentação
    if partida["status"] != "apresentacao":
        return jsonify({
            "erro": "Não é possível obter os jogadores cadastrados neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Lista todos os jogadores cadastrados
    jogadores = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "jogadores": jogadores,
        "total": len(jogadores)
    })

# Endpoint para obter os jogadores selecionados
@app.route('/api/jogadores_selecionados', methods=['GET'])
def obter_jogadores_selecionados():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "Não é possível obter os jogadores selecionados neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    # Obtém os jogadores selecionados
    jogadores_selecionados = [
        next((j for j in jogadores_disponiveis if j["id"] == id), None)
        for id in partida["configuracao"]["jogadores_selecionados"]
    ]
    
    return jsonify({
        "jogadores_selecionados": jogadores_selecionados,
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter os jogadores disponíveis
@app.route('/api/jogadores_disponiveis', methods=['GET'])
def obter_jogadores_disponiveis():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "Não é possível obter os jogadores disponíveis neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "jogadores_disponiveis": jogadores_disponiveis,
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter os jogadores não selecionados
@app.route('/api/jogadores_nao_selecionados', methods=['GET'])
def obter_jogadores_nao_selecionados():
    # Verifica se o jogo está em modo seleção
    if partida["status"] != "selecao":
        return jsonify({
            "erro": "Não é possível obter os jogadores não selecionados neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    # Obtém os jogadores não selecionados
    jogadores_nao_selecionados = [
        j for j in jogadores_disponiveis
        if j["id"] not in partida["configuracao"]["jogadores_selecionados"]
    ]
    
    return jsonify({
        "jogadores_nao_selecionados": jogadores_nao_selecionados,
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter os jogadores vencedores
@app.route('/api/jogadores_vencedores', methods=['GET'])
def obter_jogadores_vencedores():
    # Verifica se o jogo está em modo finalizado
    if partida["status"] != "finalizada":
        return jsonify({
            "erro": "Não é possível obter os jogadores vencedores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Ordena os participantes por pontuação
    ranking = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao"],
        reverse=True
    )
    
    # Obtém o vencedor
    vencedor = ranking[0] if ranking else None
    
    return jsonify({
        "vencedor": vencedor,
        "ranking": ranking,
        "ultima_partida": partida["ultima_partida"],
        "configuracao": partida["configuracao"]
    })

# Endpoint para obter os jogadores perdedores
@app.route('/api/jogadores_perdedores', methods=['GET'])
def obter_jogadores_perdedores():
    # Verifica se o jogo está em modo finalizado
    if partida["status"] != "finalizada":
        return jsonify({
            "erro": "Não é possível obter os jogadores perdedores neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Ordena os participantes por pontuação
    ranking = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao"],
        reverse=True
    )
    
    # Obtém os perdedores (todos exceto o vencedor)
    perdedores = ranking[1:] if len(ranking) > 1 else []
    
    return jsonify({
        "perdedores": perdedores,
        "ranking": ranking,
        "ultima_partida": partida["ultima_partida"],
        "configuracao": partida["configuracao"]
    })

# Endpoint para iniciar a abertura da rodada (15 segundos antes de iniciar efetivamente)
@app.route('/api/abertura_rodada', methods=['POST'])
def abertura_rodada():
    # Verifica se o jogo está iniciado
    if partida["status"] != "iniciada":
        return jsonify({
            "erro": "Não é possível iniciar a abertura de rodada neste momento",
            "status": partida["status"]
        }), 400
    
    # Se a rodada atual já é a última, não podemos avançar mais
    if partida["rodada_atual"] >= partida["total_rodadas"]:
        return jsonify({
            "erro": "Todas as rodadas já foram jogadas",
            "status": "erro"
        }), 400
    
    # Determina o número da próxima rodada
    proxima_rodada = partida["rodada_atual"] + 1
    
    # Formata o texto da próxima rodada
    texto_proxima_rodada = "FINAL" if proxima_rodada == partida["total_rodadas"] else str(proxima_rodada)
    
    # Registra a próxima rodada
    partida["proxima_rodada"] = proxima_rodada
    partida["texto_proxima_rodada"] = texto_proxima_rodada
    
    # Atualiza o status da partida para 'abertura'
    partida["status"] = "abertura"
    partida["tempo_inicio"] = time.time()
    partida["ultima_atualizacao"] = time.time()
    
    # Define o tempo da abertura (pode ser configurável)
    tempo_abertura = 15  # segundos
    
    # Prepara para a próxima rodada
    app.logger.info(f"Iniciando abertura para rodada {proxima_rodada}")
    
    # Retorna os dados da abertura
    return jsonify({
        "mensagem": f"Abertura para a rodada {texto_proxima_rodada} iniciada",
        "proxima_rodada": proxima_rodada,
        "texto_proxima_rodada": texto_proxima_rodada,
        "tempo_abertura": tempo_abertura,
        "total_rodadas": partida["total_rodadas"]
    })

# Endpoint para verificar o status da abertura
@app.route('/api/status_abertura', methods=['GET'])
def status_abertura():
    # Verifica se o jogo está em modo abertura
    if partida["status"] != "abertura":
        return jsonify({
            "erro": "Não há uma abertura de rodada em andamento",
            "status_atual": partida["status"]
        }), 400
    
    # Calcula o tempo restante
    tempo_atual = time.time()
    tempo_passado = tempo_atual - partida["tempo_inicio"]
    tempo_restante = max(0, partida["tempo_abertura"] - tempo_passado)
    
    # Se o tempo acabou, atualiza o status
    if tempo_restante <= 0:
        partida["status"] = "iniciada"
        
        return jsonify({
            "status": "concluida",
            "mensagem": "Abertura concluída, pronto para iniciar a rodada",
            "proxima_rodada": partida["proxima_rodada"],
            "total_rodadas": partida["total_rodadas"]
        })
    
    # Retorna o status da abertura
    return jsonify({
        "status": "em_andamento",
        "tempo_restante": tempo_restante,
        "tempo_total": partida["tempo_abertura"],
        "progresso": (partida["tempo_abertura"] - tempo_restante) / partida["tempo_abertura"] * 100,
        "proxima_rodada": partida["proxima_rodada"],
        "total_rodadas": partida["total_rodadas"]
    })

# Endpoint para obter o status da rodada atual
@app.route('/api/status_rodada', methods=['GET'])
def status_rodada():
    # Verifica se o jogo está em uma rodada ativa
    if partida["status"] != "rodada_ativa":
        return jsonify({
            "erro": "Não há uma rodada ativa no momento",
            "status_atual": partida["status"]
        }), 400
    
    # Calcula o tempo restante
    tempo_atual = time.time()
    tempo_passado = tempo_atual - partida["tempo_inicio"]
    tempo_restante = max(0, partida["duracao_rodada"] - tempo_passado)
    
    # Verifica se o tempo acabou
    if tempo_restante <= 0 and partida["timer_ativo"]:
        partida["timer_ativo"] = False
    
    # Obtém os dados da rodada atual
    dados_rodada = partida.get("rodada_dados", {
        "pergunta": f"Pergunta da rodada {partida['rodada_atual']}",
        "opcoes": [
            {"id": 1, "texto": "Opção A"},
            {"id": 2, "texto": "Opção B"},
            {"id": 3, "texto": "Opção C"},
            {"id": 4, "texto": "Opção D"}
        ],
        "resposta_correta": 1
    })
    
    return jsonify({
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "timer_ativo": partida["timer_ativo"],
        "tempo_restante": tempo_restante,
        "tempo_total": partida["duracao_rodada"],
        "progresso": (partida["duracao_rodada"] - tempo_restante) / partida["duracao_rodada"] * 100,
        "pergunta": dados_rodada["pergunta"],
        "opcoes": dados_rodada["opcoes"]
    })

# Endpoint para consultar as respostas dos jogadores na rodada atual
@app.route('/api/respostas_rodada', methods=['GET'])
def respostas_rodada():
    # Verifica se há respostas registradas
    if "respostas" not in partida:
        return jsonify({
            "mensagem": "Nenhuma resposta registrada ainda",
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "status": partida["status"],
            "respostas": {}
        })
    
    # Obtém dados da rodada atual
    dados_rodada = partida.get("rodada_dados", {})
    pergunta = dados_rodada.get("pergunta", "")
    opcoes = dados_rodada.get("opcoes", [])
    resposta_correta = dados_rodada.get("resposta_correta", 1)
    
    # Monta resposta com informações de cada jogador
    respostas_por_jogador = {}
    for jogador_id, resposta_info in partida["respostas"].items():
        # Busca informações do jogador
        jogador = next((j for j in partida["participantes"] if str(j["id"]) == jogador_id), None)
        if jogador:
            respostas_por_jogador[jogador_id] = {
                "jogador_id": jogador_id,
                "jogador_nome": jogador["nome"],
                "resposta": resposta_info["resposta"],
                "correta": resposta_info["correta"],
                "pontos": resposta_info["pontos"],
                "tempo": resposta_info["tempo"]
            }
    
    # Calcula estatísticas
    total_respostas = len(respostas_por_jogador)
    respostas_corretas = sum(1 for r in partida["respostas"].values() if r["correta"])
    
    return jsonify({
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "status": partida["status"],
        "pergunta": pergunta,
        "opcoes": opcoes,
        "resposta_correta": resposta_correta,
        "total_respostas": total_respostas,
        "respostas_corretas": respostas_corretas,
        "respostas": respostas_por_jogador
    })

# Endpoint para verificar o status e avançar automaticamente se necessário
@app.route('/api/verificar_avancar', methods=['GET'])
def verificar_avancar():
    # Obtém o total de rodadas da configuração
    total_rodadas = partida["configuracao"].get("total_rodadas", 10)
    
    # Verifica se uma rodada está ativa
    if partida["status"] != "rodada_ativa":
        # Determina se a rodada atual é a última
        rodada_atual_e_ultima = partida["rodada_atual"] == total_rodadas
        
        # Formata o texto da rodada atual
        # Se a rodada for 0 (partida iniciada mas sem nenhuma rodada ativa), exibir como 1
        texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else (
            "1" if partida["rodada_atual"] == 0 else str(partida["rodada_atual"])
        )
        
        return jsonify({
            "status": partida["status"],
            "avancar": False,
            "rodada_atual": partida["rodada_atual"],
            "texto_rodada_atual": texto_rodada_atual,
            "mensagem": "Não há uma rodada ativa para avançar"
        })
    
    # Tempo atual
    tempo_atual = time.time()
    
    # Verifica se o timer está ativo
    if not partida["timer_ativo"]:
        # Determina se a rodada atual é a última
        rodada_atual_e_ultima = partida["rodada_atual"] == total_rodadas
        
        # Formata o texto da rodada atual
        texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else str(partida["rodada_atual"])
        
        return jsonify({
            "status": partida["status"],
            "avancar": False,
            "rodada_atual": partida["rodada_atual"],
            "texto_rodada_atual": texto_rodada_atual,
            "mensagem": "Timer não está ativo"
        })
    
    # Calcula o tempo restante
    tempo_restante = max(0, partida["duracao_rodada"] - (tempo_atual - partida["tempo_inicio"]))
    
    # Verifica se todos os jogadores já responderam
    todos_responderam = len(partida.get("respostas_recebidas", set())) >= len(partida["participantes"])
    
    # Verifica se deve avançar (todos responderam ou tempo acabou)
    deve_avancar = todos_responderam or tempo_restante <= 0 or partida.get("avancar_rodada", False)
    
    # Determina se a próxima rodada será a última (para exibir "FINAL")
    proxima_e_ultima = (partida["rodada_atual"] + 1) == total_rodadas
    
    # Determina se a rodada atual é a última
    rodada_atual_e_ultima = partida["rodada_atual"] == total_rodadas
    
    # Formate o texto da rodada atual
    texto_rodada_atual = "FINAL" if rodada_atual_e_ultima else str(partida["rodada_atual"])
    
    # Formate o texto da próxima rodada
    texto_proxima_rodada = "FINAL" if proxima_e_ultima else str(partida["rodada_atual"] + 1)
    
    # Se deve avançar, finaliza a rodada atual e inicia a próxima
    if deve_avancar:
        # Finaliza a rodada atual com as pontuações já calculadas
        try:
            # Finaliza o timer
            partida["timer_ativo"] = False
            
            # Se a flag de avançar já estava definida, usa as pontuações já calculadas
            # Caso contrário, limpa a flag
            if "avancar_rodada" in partida:
                del partida["avancar_rodada"]
            
            # Monta o objeto de pontos a partir das respostas recebidas
            pontos = {}
            for jogador_id, resposta_info in partida.get("respostas", {}).items():
                pontos[jogador_id] = resposta_info["pontos"]
            
            # Atualiza a pontuação dos jogadores
            for jogador in partida["participantes"]:
                jogador_id = str(jogador["id"])
                if jogador_id in pontos:
                    # A pontuação já foi atualizada no endpoint de enviar_resposta,
                    # não precisamos adicionar novamente
                    pass
                else:
                    # Jogador não respondeu, adiciona 0 pontos
                    pontos[jogador_id] = 0
            
            # Muda o status para permitir iniciar uma nova rodada
            partida["status"] = "iniciada"
            partida["ultima_atualizacao"] = tempo_atual
            
            # Verifica se é a última rodada
            if partida["rodada_atual"] >= total_rodadas:
                # Determina o vencedor
                vencedor = max(partida["participantes"], key=lambda x: x["pontuacao"])
                vencedor["vitorias"] += 1
                
                # Atualiza o histórico
                partida["ultima_partida"] = {
                    "data": tempo_atual,
                    "vencedor": {
                        "id": vencedor["id"],
                        "nome": vencedor["nome"],
                        "foto": vencedor["foto"],
                        "pontuacao": vencedor["pontuacao"]
                    },
                    "pontuacao_maxima": vencedor["pontuacao"]
                }
                
                # Finaliza a partida
                partida["status"] = "finalizada"
                
                return jsonify({
                    "status": "finalizada",
                    "avancar": False,
                    "finalizada": True,
                    "mensagem": "Jogo finalizado!",
                    "rodada_atual": partida["rodada_atual"],
                    "texto_rodada_atual": texto_rodada_atual,
                    "vencedor": {
                        "id": vencedor["id"],
                        "nome": vencedor["nome"],
                        "pontuacao": vencedor["pontuacao"]
                    },
                    "participantes": partida["participantes"]
                })
            
            # Se não for a última rodada, informa que pode avançar
            proxima_rodada = partida["rodada_atual"] + 1
            
            return jsonify({
                "status": "iniciada",
                "avancar": True,
                "proxima_rodada": proxima_rodada,
                "rodada_atual": partida["rodada_atual"],
                "total_rodadas": total_rodadas,
                "texto_rodada_atual": texto_rodada_atual,
                "texto_proxima_rodada": texto_proxima_rodada,
                "mensagem": f"Rodada {texto_rodada_atual} finalizada. Pode avançar para a rodada {texto_proxima_rodada}.",
                "pontuacoes": pontos,
                "participantes": partida["participantes"]
            })
                
        except Exception as e:
            app.logger.error(f"Erro ao avançar rodada: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                "status": partida["status"],
                "avancar": False,
                "rodada_atual": partida["rodada_atual"],
                "texto_rodada_atual": texto_rodada_atual,
                "erro": str(e),
                "mensagem": "Erro ao tentar avançar para a próxima rodada"
            }), 500
    
    # Se não deve avançar, retorna o status atual
    return jsonify({
        "status": partida["status"],
        "avancar": False,
        "tempo_restante": tempo_restante,
        "tempo_total": partida["duracao_rodada"],
        "rodada_atual": partida["rodada_atual"],
        "texto_rodada_atual": texto_rodada_atual,
        "total_rodadas": total_rodadas,
        "total_respostas": len(partida.get("respostas_recebidas", set())),
        "total_jogadores": len(partida["participantes"]),
        "todos_responderam": todos_responderam,
        "mensagem": "Rodada em andamento"
    })

if __name__ == '__main__':
    # Mata qualquer processo anterior na porta 5001 (funciona apenas em sistemas Unix)
    os.system("pkill -f 'python.*app.py'")
    
    # Inicia o servidor na porta 5001
    app.run(debug=True, host='0.0.0.0', port=5001) 