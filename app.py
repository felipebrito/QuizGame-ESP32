from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time  # Importando o módulo time para controle do timer

app = Flask(__name__, static_folder='static', template_folder='templates')
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
            }
        ],
        "status": "API Quiz Game - Online",
        "version": "1.0"
    }
    
    return jsonify(endpoints)

# Dados de exemplo
perguntas = [
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
    }
]

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

@app.route('/api/status', methods=['GET'])
def status():
    # Lista todos os jogadores cadastrados para seleção
    jogadores_disponiveis = sorted(
        jogadores_cadastrados["jogadores"],
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
    return jsonify({
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "timer_ativo": partida["timer_ativo"],
        "tempo_restante": max(0, partida["duracao_rodada"] - (time.time() - partida["tempo_inicio"])) if partida["timer_ativo"] else 0,
        "duracao_rodada": partida["duracao_rodada"],
        "ultima_atualizacao": partida["ultima_atualizacao"],
        "configuracao": partida["configuracao"],
        "participantes": partida["participantes"],
        "jogadores_disponiveis": jogadores_disponiveis,
        "ultima_partida": partida["ultima_partida"],
        "historico": partida["historico"]
    })

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
        
        if partida["rodada_atual"] > partida["total_rodadas"]:
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
    # Melhorar a resposta informativa
    resposta = {
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"]
    }
    
    if partida["status"] != "rodada_ativa":
        resposta["erro"] = "Não há rodada ativa"
        resposta["mensagem"] = "É necessário iniciar o jogo e avançar para uma rodada antes de solicitar a pergunta"
        return jsonify(resposta)
    
    indice = partida["rodada_atual"] - 1
    if indice < 0 or indice >= len(perguntas):
        resposta["erro"] = "Índice de pergunta inválido"
        resposta["mensagem"] = f"Rodada {partida['rodada_atual']} não possui pergunta disponível"
        return jsonify(resposta)
    
    # Retorna pergunta sem a resposta correta
    pergunta = perguntas[indice].copy()
    pergunta_segura = {
        "id": pergunta["id"],
        "texto": pergunta["texto"],
        "tema": pergunta["tema"],
        "respostas": pergunta["respostas"]
    }
    
    # Adicionar os dados da pergunta à resposta
    resposta.update(pergunta_segura)
    
    # Adicionar informações extras para depuração
    resposta["debug"] = {
        "perguntas_disponiveis": len(perguntas),
        "indice_atual": indice
    }
    
    return jsonify(resposta)

@app.route('/api/enviar_resposta', methods=['POST'])
def enviar_resposta():
    # Corrigido para aceitar tanto dados JSON como form data
    if request.is_json:
        data = request.json
    else:
        data = request.form.to_dict()
    
    # Logging para debug
    print("Dados recebidos:", data)
    
    # Verifica se os dados necessários existem
    if not data:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
    
    # Corrigido para aceitar tanto 'resposta' quanto 'opcao'
    jogador_id = int(data.get('jogador_id', 0))
    resposta = data.get('resposta') or data.get('opcao')
    tempo = float(data.get('tempo', 0))  # Convertido para float
    
    # Validação dos dados
    if not jogador_id or not resposta:
        return jsonify({
            "erro": "Dados incompletos",
            "recebido": data
        }), 400
    
    if partida["status"] != "rodada_ativa":
        return jsonify({"erro": "Não há rodada ativa"}), 400
    
    indice = partida["rodada_atual"] - 1
    if indice < 0 or indice >= len(perguntas):
        return jsonify({"erro": "Índice de pergunta inválido"}), 400
        
    pergunta = perguntas[indice]
    
    # Localizar jogador
    jogador = None
    for p in partida["participantes"]:
        if p["id"] == jogador_id:
            jogador = p
            break
    
    if not jogador:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
    # Verificar resposta
    eh_correta = resposta == pergunta["resposta_correta"]
    
    # Atualizar pontuação (resposta correta: 10 pontos base)
    pontos = 0
    if eh_correta:
        pontos = 10
        # Bônus por velocidade (máximo 5 pontos extras)
        if tempo < 1000:  # menos de 1 segundo
            pontos += 5
        elif tempo < 3000:  # menos de 3 segundos
            pontos += 3
        elif tempo < 5000:  # menos de 5 segundos
            pontos += 1
            
        jogador["pontuacao"] += pontos
    
    return jsonify({
        "correta": eh_correta,
        "pontos_obtidos": pontos if eh_correta else 0,
        "pontuacao_total": jogador["pontuacao"],
        "jogador": jogador["nome"]
    })

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
    
    # Opcionalmente recebe mensagem personalizada
    mensagem = dados.get("mensagem", "Quiz Game - Aguardando início da partida")
    tema = dados.get("tema", "default")
    
    # Ranking global (ordenado por pontuação total)
    ranking_global = sorted(
        jogadores_cadastrados["jogadores"],  # Usando os jogadores cadastrados ao invés dos participantes
        key=lambda x: x["pontuacao_total"],
        reverse=True
    )
    
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
    temas = set(p["tema"] for p in perguntas)
    
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
    dados = request.json if request.is_json else {}
    
    # Validação dos jogadores selecionados
    jogadores_selecionados = dados.get("jogadores", [])
    if len(jogadores_selecionados) != 3:
        return jsonify({
            "erro": "É necessário selecionar exatamente 3 jogadores",
            "status": "erro"
        }), 400
    
    # Validação da duração da rodada
    duracao = float(dados.get("duracao_rodada", 30.0))
    if duracao < 10 or duracao > 60:
        return jsonify({
            "erro": "A duração da rodada deve estar entre 10 e 60 segundos",
            "status": "erro"
        }), 400
    
    # Validação do número de rodadas
    total_rodadas = int(dados.get("total_rodadas", 10))
    if total_rodadas < 5 or total_rodadas > 20:
        return jsonify({
            "erro": "O número de rodadas deve estar entre 5 e 20",
            "status": "erro"
        }), 400
    
    # Atualiza a configuração
    partida["configuracao"].update({
        "jogadores_selecionados": jogadores_selecionados,
        "duracao_rodada": duracao,
        "total_rodadas": total_rodadas,
        "tema": dados.get("tema", "default"),
        "status": "validada"
    })
    
    # Atualiza os parâmetros globais da partida
    partida["total_rodadas"] = total_rodadas
    partida["duracao_rodada"] = duracao
    
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
    # Verifica se o jogo está em modo aguardando
    if partida["status"] != "aguardando":
        return jsonify({
            "erro": "Não é possível iniciar a partida neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Verifica se a configuração está validada
    if partida["configuracao"]["status"] != "validada":
        return jsonify({
            "erro": "A configuração da partida não está validada",
            "status": "erro"
        }), 400
    
    # Obtém os jogadores selecionados
    jogadores_selecionados = partida["configuracao"]["jogadores_selecionados"]
    
    # Inicializa os participantes com os jogadores selecionados
    partida["participantes"] = [
        {
            "id": id,
            "nome": next((j["nome"] for j in jogadores_cadastrados["jogadores"] if j["id"] == id), "Jogador Desconhecido"),
            "foto": next((j["foto"] for j in jogadores_cadastrados["jogadores"] if j["id"] == id), "https://randomuser.me/api/portraits/lego/0.jpg"),
            "pontuacao": 0,
            "pontuacao_total": next((j["pontuacao_total"] for j in jogadores_cadastrados["jogadores"] if j["id"] == id), 0),
            "partidas_jogadas": next((j["partidas_jogadas"] for j in jogadores_cadastrados["jogadores"] if j["id"] == id), 0),
            "vitorias": next((j["vitorias"] for j in jogadores_cadastrados["jogadores"] if j["id"] == id), 0)
        }
        for id in jogadores_selecionados
    ]
    
    # Inicializa a partida
    partida["status"] = "iniciada"
    partida["rodada_atual"] = 0
    partida["timer_ativo"] = False
    partida["tempo_inicio"] = 0
    partida["ultima_atualizacao"] = time.time()
    partida["configuracao"]["status"] = "iniciada"
    
    # Atualiza o histórico dos jogadores
    for jogador in partida["participantes"]:
        jogador["partidas_jogadas"] += 1
    
    return jsonify({
        "mensagem": "Partida iniciada com sucesso",
        "status": "iniciada",
        "participantes": partida["participantes"]
    })

# Endpoint para resetar o jogo
@app.route('/api/reset', methods=['POST'])
def reset():
    # Reseta a partida para o estado inicial
    partida["status"] = "apresentacao"
    partida["rodada_atual"] = 0
    partida["timer_ativo"] = False
    partida["tempo_inicio"] = 0
    partida["ultima_atualizacao"] = time.time()
    partida["configuracao"] = {
        "jogadores_selecionados": [],
        "duracao_rodada": 30.0,
        "total_rodadas": 10,
        "tema": "default",
        "status": "pendente"
    }
    partida["participantes"] = []
    
    return jsonify({
        "mensagem": "Jogo resetado com sucesso",
        "status": "apresentacao"
    })

# Endpoint para iniciar uma nova rodada
@app.route('/api/iniciar_rodada', methods=['POST'])
def iniciar_rodada():
    # Verifica se o jogo está iniciado
    if partida["status"] != "iniciada":
        return jsonify({
            "erro": "Não é possível iniciar uma rodada neste momento",
            "status_atual": partida["status"]
        }), 400
    
    # Verifica se já não está em uma rodada
    if partida["status"] == "rodada_ativa":
        return jsonify({
            "erro": "Já existe uma rodada em andamento",
            "status": "erro"
        }), 400
    
    # Verifica se ainda há rodadas disponíveis
    if partida["rodada_atual"] >= partida["total_rodadas"]:
        return jsonify({
            "erro": "Todas as rodadas já foram jogadas",
            "status": "erro"
        }), 400
    
    # Inicia a rodada
    partida["status"] = "rodada_ativa"
    partida["rodada_atual"] += 1
    partida["timer_ativo"] = True
    partida["tempo_inicio"] = time.time()
    partida["ultima_atualizacao"] = time.time()
    
    return jsonify({
        "mensagem": f"Rodada {partida['rodada_atual']} iniciada",
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "duracao_rodada": partida["duracao_rodada"]
    })

# Endpoint para finalizar a rodada atual
@app.route('/api/finalizar_rodada', methods=['POST'])
def finalizar_rodada():
    # Verifica se o jogo está em uma rodada ativa
    if partida["status"] != "rodada_ativa":
        return jsonify({
            "erro": "Não há uma rodada ativa para finalizar",
            "status_atual": partida["status"]
        }), 400
    
    # Obtém os dados da rodada
    dados = request.json if request.is_json else {}
    
    # Validação dos pontos
    pontos = dados.get("pontos", {})
    if not pontos or len(pontos) != len(partida["participantes"]):
        return jsonify({
            "erro": "É necessário fornecer pontos para todos os participantes",
            "status": "erro"
        }), 400
    
    # Atualiza a pontuação dos participantes
    for jogador in partida["participantes"]:
        jogador["pontuacao"] += pontos.get(str(jogador["id"]), 0)
        jogador["pontuacao_total"] += pontos.get(str(jogador["id"]), 0)
    
    # Finaliza a rodada
    partida["status"] = "iniciada"
    partida["timer_ativo"] = False
    partida["ultima_atualizacao"] = time.time()
    
    # Verifica se é a última rodada
    if partida["rodada_atual"] >= partida["total_rodadas"]:
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
        
        # Atualiza o recorde
        if vencedor["pontuacao"] > partida["historico"]["recorde_pontos"]:
            partida["historico"]["recorde_pontos"] = vencedor["pontuacao"]
            partida["historico"]["recordista"] = {
                "id": vencedor["id"],
                "nome": vencedor["nome"],
                "foto": vencedor["foto"]
            }
        
        partida["historico"]["total_partidas"] += 1
        
        # Finaliza a partida
        partida["status"] = "finalizada"
    
    return jsonify({
        "mensagem": f"Rodada {partida['rodada_atual']} finalizada",
        "status": partida["status"],
        "participantes": partida["participantes"],
        "ultima_partida": partida["ultima_partida"] if partida["status"] == "finalizada" else None
    })

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
    
    return jsonify({
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 