from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os
import random
import json
import time
import requests
from pythonosc import udp_client
import sqlite3
from datetime import datetime
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')
# Modificando a configuração do Jinja2 para permitir operadores ternários
app.jinja_env.variable_start_string = '{['  # Alterando de {{ para {[
app.jinja_env.variable_end_string = ']}'    # Alterando de }} para ]}
CORS(app)

# Cliente OSC para enviar mensagens ao Chataigne
osc_client = udp_client.SimpleUDPClient("192.168.1.36", 3333)  # IP e porta do Chataigne

# Variáveis globais do jogo
todas_perguntas = []
perguntas_selecionadas = []
jogadores_cadastrados = []
modo_atual = "apresentacao"  # apresentacao, selecao, aguardando, ativo, finalizado
tema_atual = "default"
status_jogo = "apresentacao"  # status para enviar via OSC: apresentacao, selecao, preparacao, jogando, rodada_ativa, rodada_finalizada, jogo_finalizado

# Configuração inicial da partida
partida = {
    "status": "aguardando",
    "participantes": [],
    "rodada_atual": 0,
    "total_rodadas": 0,
    "duracao_rodada": 30.0,
    "tema": "default",
    "perguntas_selecionadas": [],
    "respostas_recebidas": set(),
    "respostas": {}
}

# Configuração do banco de dados SQLite
DATABASE_FILE = 'quiz_game.db'

def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias se não existirem"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Criar tabela de histórico de partidas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            total_jogadores INTEGER NOT NULL,
            total_rodadas INTEGER NOT NULL,
            duracao_rodada REAL NOT NULL,
            vencedor_id INTEGER,
            vencedor_nome TEXT,
            vencedor_pontuacao INTEGER,
            status TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
        ''')
        
        # Criar tabela de detalhes dos participantes por partida
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS participantes_partida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            jogador_id INTEGER NOT NULL,
            jogador_nome TEXT NOT NULL,
            posicao INTEGER NOT NULL,
            pontuacao INTEGER NOT NULL,
            FOREIGN KEY (partida_id) REFERENCES partidas (id)
        )
        ''')
        
        # Criar tabela de respostas por rodada
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas_rodada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            rodada INTEGER NOT NULL,
            jogador_id INTEGER NOT NULL,
            pergunta_id INTEGER NOT NULL,
            resposta INTEGER,
            correta INTEGER NOT NULL,
            tempo_resposta REAL,
            pontos_obtidos INTEGER NOT NULL,
            FOREIGN KEY (partida_id) REFERENCES partidas (id)
        )
        ''')
        
        conn.commit()
        app.logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        app.logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def registrar_partida(participantes, total_rodadas, duracao_rodada):
    """Registra uma nova partida no banco de dados e retorna o ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = time.time()
        
        cursor.execute('''
        INSERT INTO partidas 
        (data_hora, total_jogadores, total_rodadas, duracao_rodada, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (agora, len(participantes), total_rodadas, duracao_rodada, 'iniciada', timestamp))
        
        partida_id = cursor.lastrowid
        
        # Registrar participantes
        for i, participante in enumerate(participantes, 1):
            cursor.execute('''
            INSERT INTO participantes_partida
            (partida_id, jogador_id, jogador_nome, posicao, pontuacao)
            VALUES (?, ?, ?, ?, ?)
            ''', (partida_id, participante['id'], participante['nome'], i, 0))
        
        conn.commit()
        app.logger.info(f"Nova partida registrada com ID {partida_id}")
        return partida_id
    except Exception as e:
        app.logger.error(f"Erro ao registrar partida: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()

def atualizar_status_partida(partida_id, status, vencedor=None):
    """Atualiza o status de uma partida e, se finalizada, registra o vencedor"""
    if not partida_id:
        return False
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        if vencedor and status == 'finalizada':
            cursor.execute('''
            UPDATE partidas SET 
            status = ?, vencedor_id = ?, vencedor_nome = ?, vencedor_pontuacao = ?
            WHERE id = ?
            ''', (status, vencedor['id'], vencedor['nome'], vencedor['pontuacao'], partida_id))
        else:
            cursor.execute('''
            UPDATE partidas SET status = ? WHERE id = ?
            ''', (status, partida_id))
        
        conn.commit()
        app.logger.info(f"Status da partida {partida_id} atualizado para: {status}")
        return True
    except Exception as e:
        app.logger.error(f"Erro ao atualizar status da partida: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def registrar_resposta(partida_id, rodada, jogador_id, pergunta_id, resposta, correta, tempo_resposta, pontos_obtidos):
    """Registra uma resposta de jogador no banco de dados"""
    if not partida_id:
        return False
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO respostas_rodada
        (partida_id, rodada, jogador_id, pergunta_id, resposta, correta, tempo_resposta, pontos_obtidos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (partida_id, rodada, jogador_id, pergunta_id, resposta, 1 if correta else 0, tempo_resposta, pontos_obtidos))
        
        conn.commit()
        app.logger.info(f"Resposta registrada: jogador {jogador_id} na rodada {rodada} da partida {partida_id}")
        return True
    except Exception as e:
        app.logger.error(f"Erro ao registrar resposta: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def atualizar_pontuacao_jogador(partida_id, jogador_id, pontuacao):
    """Atualiza a pontuação de um jogador em uma partida específica"""
    if not partida_id:
        return False
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE participantes_partida SET pontuacao = ?
        WHERE partida_id = ? AND jogador_id = ?
        ''', (pontuacao, partida_id, jogador_id))
        
        conn.commit()
        app.logger.info(f"Pontuação do jogador {jogador_id} atualizada para {pontuacao} na partida {partida_id}")
        return True
    except Exception as e:
        app.logger.error(f"Erro ao atualizar pontuação: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Inicializar o logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variável para armazenar o ID da partida atual
partida_db_id = None

# Inicializar perguntas para o jogo
def load_perguntas():
    # Esta função seria implementada para carregar perguntas de um arquivo
    # Por simplicidade, apenas retornaremos uma lista estática de exemplo
    return [
        {
            "id": 1,
            "pergunta": "Qual a capital do Brasil?",
            "opcoes": ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
            "resposta_correta": 3,
            "categoria": "Geografia",
            "dificuldade": "Fácil"
        },
        {
            "id": 2,
            "pergunta": "Quem escreveu 'Dom Casmurro'?",
            "opcoes": ["José de Alencar", "Machado de Assis", "Carlos Drummond de Andrade", "Clarice Lispector"],
            "resposta_correta": 2,
            "categoria": "Literatura",
            "dificuldade": "Médio"
        },
        {
            "id": 3,
            "pergunta": "Qual é a capital do Japão?",
            "opcoes": ["Pequim", "Seul", "Tóquio", "Bangkok"],
            "resposta_correta": 3,
            "categoria": "Geografia",
            "dificuldade": "Fácil"
        },
        {
            "id": 4,
            "pergunta": "Qual é o maior planeta do sistema solar?",
            "opcoes": ["Terra", "Marte", "Júpiter", "Saturno"],
            "resposta_correta": 3,
            "categoria": "Astronomia",
            "dificuldade": "Fácil"
        },
        {
            "id": 5,
            "pergunta": "Qual o símbolo químico do ouro?",
            "opcoes": ["Au", "Ag", "Fe", "O"],
            "resposta_correta": 1,
            "categoria": "Química",
            "dificuldade": "Médio"
        },
        {
            "id": 6,
            "pergunta": "Em que ano ocorreu a Independência do Brasil?",
            "opcoes": ["1808", "1822", "1889", "1500"],
            "resposta_correta": 2,
            "categoria": "História",
            "dificuldade": "Médio"
        }
    ]

# Função para obter o status atual do jogo
def obter_status_atual():
    return {
        "modo": modo_atual,
        "tema": tema_atual,
        "partida_status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "jogadores_disponiveis": len(jogadores_cadastrados),
        "participantes_ativos": len(partida["participantes"])
    }

# Carregar perguntas
todas_perguntas = load_perguntas()

# Rotas da aplicação
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/websocket', methods=['GET'])
def websocket_client():
    return render_template('websocket_client.html')

# Endpoint para receber respostas dos jogadores via HTTP
@app.route('/api/enviar_resposta', methods=['POST'])
def enviar_resposta_http_route():
    """Endpoint para receber respostas dos jogadores via HTTP"""
    try:
        app.logger.info(f"Recebendo resposta via HTTP - Args: {request.args}, Form: {request.form}, JSON: {request.is_json}")
        
        # Primeiro, verificar se os dados estão nos argumentos URL ou form data
        jogador = None
        resposta = None
        tempo = 0
        tempo_decorrido = 0  # Inicialização da variável tempo_decorrido com valor padrão
        
        # Verificar primeiro no form data
        if 'jogador' in request.form:
            jogador = request.form.get('jogador')
            app.logger.info(f"Jogador extraído do form: {jogador}")
        
        if 'resposta' in request.form:
            resposta_raw = request.form.get('resposta')
            app.logger.info(f"Resposta extraída do form: {resposta_raw}")
            
            # Converter resposta para formato numérico
            if resposta_raw.upper() == 'A':
                resposta = 1
            elif resposta_raw.upper() == 'B':
                resposta = 2
            elif resposta_raw.upper() == 'C':
                resposta = 3
            elif resposta_raw.upper() == 'D':
                resposta = 4
            else:
                try:
                    resposta = int(resposta_raw)
                except:
                    app.logger.error(f"Formato de resposta inválido: {resposta_raw}")
                    return jsonify({"status": "erro", "erro": f"Formato de resposta inválido: {resposta_raw}"}), 400
        
        # Se não encontrou no form data, verificar nos argumentos da URL
        if jogador is None and 'jogador' in request.args:
            jogador = request.args.get('jogador')
            app.logger.info(f"Jogador extraído dos args: {jogador}")
        
        if resposta is None and 'resposta' in request.args:
            resposta_raw = request.args.get('resposta')
            app.logger.info(f"Resposta extraída dos args: {resposta_raw}")
            
            # Converter resposta para formato numérico
            if resposta_raw.upper() == 'A':
                resposta = 1
            elif resposta_raw.upper() == 'B':
                resposta = 2
            elif resposta_raw.upper() == 'C':
                resposta = 3
            elif resposta_raw.upper() == 'D':
                resposta = 4
            else:
                try:
                    resposta = int(resposta_raw)
                except:
                    app.logger.error(f"Formato de resposta inválido: {resposta_raw}")
                    return jsonify({"status": "erro", "erro": f"Formato de resposta inválido: {resposta_raw}"}), 400
                    
        # Verificar tempo em ambos os lugares
        if 'tempo' in request.form:
            try:
                tempo = float(request.form.get('tempo'))
            except:
                app.logger.warning(f"Formato de tempo inválido no form: {request.form.get('tempo')}")
        elif 'tempo' in request.args:
            try:
                tempo = float(request.args.get('tempo'))
            except:
                app.logger.warning(f"Formato de tempo inválido nos args: {request.args.get('tempo')}")
        
        # Se não encontramos os parâmetros, retornar erro
        if jogador is None or resposta is None:
            app.logger.error("Faltando parâmetros obrigatórios: jogador e resposta")
            return jsonify({"status": "erro", "erro": "Faltando parâmetros: jogador e resposta são obrigatórios"}), 400
                
        # Converter posição do jogador para ID
        try:
            jogador_posicao = int(jogador)
            if jogador_posicao < 1 or jogador_posicao > len(partida["participantes"]):
                app.logger.error(f"Posição de jogador inválida: {jogador_posicao}")
                return jsonify({"status": "erro", "erro": f"Posição de jogador inválida: {jogador_posicao}"}), 400
                
            # Obter o ID real do jogador com base na posição
            jogador_id = str(partida["participantes"][jogador_posicao - 1]["id"])
            app.logger.info(f"Convertendo posição {jogador_posicao} para jogador_id {jogador_id}")
        except Exception as e:
            app.logger.error(f"Erro ao converter posição de jogador: {str(e)}")
            return jsonify({"status": "erro", "erro": f"Erro ao identificar jogador: {str(e)}"}), 400
        
        # Obter dados do jogador
        nome_jogador = obter_nome_jogador(jogador_id)
        if not nome_jogador:
            app.logger.error(f"Jogador {jogador_id} não encontrado")
            return jsonify({"status": "erro", "erro": f"Jogador {jogador_id} não encontrado"}), 400
            
        # Verificar status do jogo
        if partida["status"] != "rodada_ativa":
            app.logger.error(f"Não há rodada ativa no momento. Status atual: {partida['status']}")
            return jsonify({
                "status": "erro", 
                "erro": "Não há uma rodada ativa no momento",
                "status_atual": partida["status"]
            }), 400
            
        # Verificar se o jogador já respondeu
        if jogador_id in partida["respostas_recebidas"]:
            app.logger.error(f"Jogador {nome_jogador} já respondeu esta pergunta")
            return jsonify({"status": "erro", "erro": f"Jogador {nome_jogador} já respondeu esta pergunta"}), 400
            
        # Registrar a resposta
        app.logger.info(f"Jogador {nome_jogador} (ID {jogador_id}) respondeu {resposta}")
        partida["respostas_recebidas"].add(jogador_id)
        
        # Calcular a pontuação
        pontos = 0
        rodada_atual = partida["rodada_atual"]
        pergunta_atual = partida["pergunta_atual"]
        pergunta_id = pergunta_atual["id"]
        resposta_correta = pergunta_atual["resposta_correta"]
        correta = resposta == resposta_correta
        
        # Se a resposta estiver correta, calcular pontuação com base no tempo
        if correta:
            try:
                # Verificar se existe 'inicio_rodada' ou 'tempo_inicio' no dicionário partida
                if "inicio_rodada" in partida:
                    tempo_decorrido = tempo if tempo > 0 else (time.time() - partida["inicio_rodada"])
                elif "tempo_inicio" in partida:
                    tempo_decorrido = tempo if tempo > 0 else (time.time() - partida["tempo_inicio"])
                else:
                    # Se nenhum existe, usar o tempo atual menos 1 segundo como fallback
                    app.logger.warning("Chave 'inicio_rodada' e 'tempo_inicio' não encontradas no dicionário partida. Usando fallback.")
                    tempo_decorrido = tempo if tempo > 0 else 1  # Assume 1 segundo como padrão
            except Exception as e:
                app.logger.error(f"Erro ao calcular tempo decorrido: {str(e)}")
                tempo_decorrido = tempo if tempo > 0 else 1  # Fallback em caso de erro
                
            tempo_total = partida["duracao_rodada"]
            
            # Quanto mais rápido responder, mais pontos ganha
            fator_tempo = 1 - (tempo_decorrido / tempo_total)
            
            # Garantir que o fator de tempo esteja entre 0 e 1
            fator_tempo = max(0, min(1, fator_tempo))
            
            # Cálculo de pontos: base de 50 pontos + até 50 pontos por rapidez
            pontos = 50 + int(50 * fator_tempo)
        else:
            # Caso a resposta seja incorreta, certifique-se de que tempo_decorrido tenha um valor
            if tempo > 0:
                tempo_decorrido = tempo
            elif "inicio_rodada" in partida:
                tempo_decorrido = time.time() - partida["inicio_rodada"]
            elif "tempo_inicio" in partida:
                tempo_decorrido = time.time() - partida["tempo_inicio"]
            # Já temos um valor padrão definido no início da função
            
        # Registrar a resposta no objeto partida
        if "respostas" not in partida:
            partida["respostas"] = {}
            
        partida["respostas"][jogador_id] = {
            "resposta": resposta,
            "correta": correta,
            "tempo": tempo_decorrido,
            "pontos": pontos
        }
        
        # Atualizar a pontuação do jogador
        for participante in partida["participantes"]:
            if str(participante["id"]) == jogador_id:
                participante["pontuacao"] += pontos
                break
                
        # Registrar a resposta no banco de dados
        global partida_db_id
        if partida_db_id:
            app.logger.info(f"Registrando resposta no banco de dados para partida {partida_db_id}")
            try:
                registrar_resposta(
                    partida_db_id,
                    rodada_atual,
                    int(jogador_id),
                    pergunta_id,
                    resposta,
                    correta,
                    tempo_decorrido,
                    pontos
                )
                
                # Também atualizar a pontuação do jogador no banco de dados
                for participante in partida["participantes"]:
                    if str(participante["id"]) == jogador_id:
                        atualizar_pontuacao_jogador(
                            partida_db_id,
                            int(jogador_id),
                            participante["pontuacao"]
                        )
                        break
                        
                app.logger.info(f"Resposta e pontuação registradas no banco de dados com sucesso")
            except Exception as e:
                app.logger.error(f"Erro ao registrar no banco de dados: {str(e)}")
                import traceback
                app.logger.error(traceback.format_exc())
        else:
            app.logger.warning("Não foi possível registrar a resposta no banco de dados: partida_db_id não definido")
                
        # Calcular o ranking atual
        ranking = calcular_ranking_atual()
        
        # Verificar se todos os jogadores já responderam
        todos_responderam = len(partida["respostas_recebidas"]) >= len(partida["participantes"])
        
        # Enviar mensagem via OSC
        try:
            # Informar qual jogador respondeu
            osc_client.send_message(f"/quiz/resposta/jogador_id", jogador_id)
            osc_client.send_message(f"/quiz/resposta/jogador_nome", nome_jogador)
            osc_client.send_message(f"/quiz/resposta/correta", 1 if correta else 0)
            osc_client.send_message(f"/quiz/resposta/pontos", pontos)
            osc_client.send_message(f"/quiz/jogador{jogador_posicao}", 1 if correta else 0)
            
            # Informar quantas respostas já recebemos
            osc_client.send_message("/quiz/partida/respostas", len(partida["respostas_recebidas"]))
            
            # Enviar o ranking atualizado
            for i, r in enumerate(ranking):
                pos = i + 1
                osc_client.send_message(f"/quiz/partida/jogador{pos}/nome", r["nome"])
                osc_client.send_message(f"/quiz/partida/jogador{pos}/pontos", r["pontuacao"])
                osc_client.send_message(f"/quiz/partida/jogador{pos}/posicao", pos)
                osc_client.send_message(f"/quiz/partida/jogador{pos}/id", r["id"])
                
            # Se todos responderam, enviar um trigger para finalizar a rodada
            if todos_responderam:
                enviar_trigger_finaliza_rodada_osc()
                
        except Exception as e:
            app.logger.error(f"Erro ao enviar mensagem OSC: {str(e)}")
            
        # Retornar o resultado
        return jsonify({
            "status": "ok",
            "jogador_id": jogador_id,
            "jogador_nome": nome_jogador,
            "jogador_posicao": jogador_posicao,
            "pergunta": partida["pergunta_atual"]["pergunta"],
            "resposta": resposta,
            "resposta_correta": resposta_correta,
            "correta": correta,
            "pontos_obtidos": pontos,
            "pontuacao_total": next((p["pontuacao"] for p in partida["participantes"] if str(p["id"]) == jogador_id), 0),
            "ranking_atual": ranking,
            "total_respostas": len(partida["respostas_recebidas"]),
            "total_jogadores": len(partida["participantes"]),
            "todos_responderam": todos_responderam
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar resposta: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"status": "erro", "erro": f"Erro ao processar resposta: {str(e)}"}), 500

def enviar_resposta_http(jogador_id, resposta, tempo=0):
    """
    Processa a resposta recebida de um jogador via HTTP.
    
    Args:
        jogador_id (int): ID do jogador
        resposta (int): Resposta do jogador (1-4)
        tempo (float, optional): Tempo de resposta em segundos. Padrão: 0.
        
    Returns:
        dict: Resultado do processamento da resposta
    """
    global partida, partida_db_id
    
    # Verificar se há uma partida em andamento
    if partida["status"] != "rodada_ativa":
        app.logger.warning(f"Resposta recebida, mas não há rodada ativa (status: {partida['status']})")
        return {
            "status": "erro",
            "erro": "Não há rodada ativa para receber respostas",
            "jogador_id": jogador_id
        }
    
    # Procurar o jogador na lista de participantes
    jogador = None
    jogador_posicao = 0
    for i, participante in enumerate(partida["participantes"], 1):
        if participante["id"] == jogador_id:
            jogador = participante
            jogador_posicao = i
            break
    
    if not jogador:
        app.logger.warning(f"Jogador {jogador_id} não está participando da partida")
        return {
            "status": "erro",
            "erro": "Jogador não está participando da partida",
            "jogador_id": jogador_id
        }
    
    # Verificar se o jogador já respondeu
    if jogador_id in partida["respostas_recebidas"]:
        app.logger.warning(f"Jogador {jogador_id} já enviou resposta para esta rodada")
        return {
            "status": "erro",
            "erro": "Jogador já enviou resposta para esta rodada",
            "jogador_id": jogador_id
        }
    
    # Registrar a resposta do jogador
    rodada_atual = partida["rodada_atual"]
    pergunta_id = partida["perguntas_selecionadas"][rodada_atual - 1]["id"]
    resposta_correta = partida["perguntas_selecionadas"][rodada_atual - 1]["resposta_correta"]
    correta = (resposta == resposta_correta)
    
    app.logger.info(f"Jogador {jogador_id} respondeu {resposta} (correta: {resposta_correta})")
    
    # Calcular tempo de resposta e pontuação
    try:
        if tempo == 0 and "inicio_rodada" in partida:
            tempo_decorrido = time.time() - partida["inicio_rodada"]
        else:
            tempo_decorrido = tempo
    except KeyError:
        # Tratar caso de chave ausente
        app.logger.warning("Chave 'tempo_inicio' ou 'inicio_rodada' ausente no dicionário da partida")
        tempo_decorrido = partida["duracao_rodada"] / 2  # valor padrão médio
    
    # Clamp no tempo entre 0 e a duração da rodada
    tempo_decorrido = max(0, min(tempo_decorrido, partida["duracao_rodada"]))
    
    # Calcular pontuação
    pontos_base = 100
    
    # Bônus por tempo: quanto mais rápido, mais pontos (máximo 100, mínimo 0)
    bonus_tempo = int((1 - (tempo_decorrido / partida["duracao_rodada"])) * 100)
    
    # Pontuação final
    pontos_obtidos = pontos_base + bonus_tempo if correta else 0
    
    # Adicionar a resposta ao registro da partida
    partida["respostas"][jogador_id] = {
        "resposta": resposta,
        "correta": correta,
        "tempo": tempo_decorrido,
        "pontos": pontos_obtidos
    }
    
    # Adicionar o jogador ao conjunto de respostas recebidas
    partida["respostas_recebidas"].add(jogador_id)
    
    # Atualizar a pontuação do jogador
    jogador["pontuacao"] += pontos_obtidos
    
    # Registrar a resposta no banco de dados
    try:
        if partida_db_id:
            registrar_resposta(
                partida_db_id,
                rodada_atual,
                jogador_id,
                pergunta_id,
                resposta,
                correta,
                tempo_decorrido,
                pontos_obtidos
            )
            
            # Atualizar a pontuação do jogador no banco de dados
            atualizar_pontuacao_jogador(
                partida_db_id,
                jogador_id,
                jogador["pontuacao"]
            )
    except Exception as e:
        app.logger.error(f"Erro ao registrar resposta no banco de dados: {str(e)}")
    
    # Preparar dados de resposta para enviar via OSC
    dados_resposta = {
        "jogador_id": jogador_id,
        "jogador_nome": jogador["nome"],
        "jogador_posicao": jogador_posicao,
        "resposta": resposta,
        "correta": correta,
        "tempo_resposta": tempo_decorrido,
        "pontos_obtidos": pontos_obtidos,
    }
    
    # Enviar dados da resposta via OSC
    enviar_resposta_osc(dados_resposta)
    
    # Verificar se todos os jogadores já responderam
    if len(partida["respostas_recebidas"]) == len(partida["participantes"]):
        # Finalizar a rodada automaticamente
        app.logger.info("Todos os jogadores já responderam, finalizando a rodada")
        finalizar_rodada_atual()
    
    # Calcular a posição atual (ranking)
    participantes_ordenados = sorted(
        partida["participantes"],
        key=lambda x: x["pontuacao"],
        reverse=True
    )
    posicao_atual = participantes_ordenados.index(jogador) + 1
    
    return {
        "status": "ok",
        "jogador_id": jogador_id,
        "jogador_nome": jogador["nome"],
        "resposta": resposta,
        "correta": correta,
        "pontos_obtidos": pontos_obtidos,
        "pontuacao_total": jogador["pontuacao"],
        "posicao_atual": posicao_atual,
        "total_respostas": len(partida["respostas_recebidas"]),
        "total_jogadores": len(partida["participantes"])
    }
    
# Função para finalizar a rodada atual
def finalizar_rodada_atual():
    """
    Finaliza a rodada atual e verifica se a partida acabou.
    """
    global partida, status_jogo, partida_db_id
    
    app.logger.info(f"Finalizando rodada {partida['rodada_atual']}")
    
    # Verificar se a rodada atual é a última
    if partida["rodada_atual"] >= partida["total_rodadas"]:
        # Esta foi a última rodada, finalizar o jogo
        status_jogo = "jogo_finalizado"
        partida["status"] = "finalizado"
        
        app.logger.info("Última rodada finalizada, jogo completo")
        
        # Encontrar o vencedor
        vencedor = max(partida["participantes"], key=lambda x: x["pontuacao"])
        
        app.logger.info(f"Vencedor: {vencedor['nome']} com {vencedor['pontuacao']} pontos")
        
        # Atualizar o banco de dados
        try:
            if partida_db_id:
                atualizar_status_partida(
                    partida_db_id,
                    'finalizada',
                    {
                        'id': vencedor["id"],
                        'nome': vencedor["nome"],
                        'pontuacao': vencedor["pontuacao"]
                    }
                )
        except Exception as e:
            app.logger.error(f"Erro ao atualizar status da partida no banco de dados: {str(e)}")
        
        # Atualizar as pontuações totais dos jogadores
        atualizar_pontuacoes_finais()
        
        # Ordenar participantes por pontuação (ranking final)
        ranking_final = sorted(
            partida["participantes"],
            key=lambda x: x["pontuacao"],
            reverse=True
        )
        
        # Enviar informações do final do jogo via OSC
        enviar_final_osc(vencedor, ranking_final)
    else:
        # Ainda tem rodadas restantes
        status_jogo = "rodada_finalizada"
        partida["status"] = "aguardando_rodada"
        
        # Atualizar o banco de dados
        try:
            if partida_db_id:
                atualizar_status_partida(partida_db_id, 'rodada_finalizada')
        except Exception as e:
            app.logger.error(f"Erro ao atualizar status da partida no banco de dados: {str(e)}")
    
    # Limpar as respostas recebidas para a próxima rodada
    partida["respostas_recebidas"] = set()
    
    # Enviar status do jogo via OSC
    enviar_status_jogo_osc()
    
    app.logger.info(f"Rodada finalizada. Status atualizado para: {status_jogo}")

@app.route('/api/verificar_avancar', methods=['GET', 'POST'])
def verificar_avancar():
    """
    Verifica se deve avançar para a próxima rodada e atualiza o status do jogo.
    """
    global status_jogo
    
    # Verifica se deve avançar para a próxima rodada
    if partida.get("avancar_rodada", False) or request.method == 'POST':
        partida["avancar_rodada"] = False
        partida["status"] = "aguardando_rodada"
        status_jogo = "rodada_finalizada"
        
        # Verificar se todos responderam
        total_respostas = len(partida.get("respostas_recebidas", set()))
        total_jogadores = len(partida["participantes"])
        
        app.logger.info(f"Verificando avanço: {total_respostas}/{total_jogadores} jogadores responderam")
        
        # Enviar status do jogo via OSC
        enviar_status_jogo_osc()
        
        # Enviar pontuações atuais
        enviar_pontuacoes_atuais_osc()
        
        # Enviar trigger de reset para o próximo round
        osc_client.send_message("/quiz/trigger/finaliza_rodada", 0)
        
        return jsonify({
            "avancar": True,
            "status": partida["status"],
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "total_respostas": total_respostas,
            "total_jogadores": total_jogadores,
            "participantes": [
                {
                    "id": p["id"],
                    "nome": p["nome"],
                    "pontuacao": p["pontuacao"]
                } for p in sorted(partida["participantes"], key=lambda x: x["pontuacao"], reverse=True)
            ]
        })
    
    # Verifica se o jogo foi finalizado
    if partida["status"] == "finalizada":
        status_jogo = "jogo_finalizado"
        
        # Obtem o jogador vencedor
        vencedor = None
        ranking_final = []
        
        if partida["participantes"]:
            ranking_final = sorted(partida["participantes"], key=lambda x: x["pontuacao"], reverse=True)
            vencedor = ranking_final[0] if ranking_final else None
            
            # Enviar resultado final via OSC
            if vencedor:
                enviar_final_osc(vencedor, ranking_final)
                
            # Atualizar pontuações totais no banco de dados
            atualizar_pontuacoes_finais()
        
        # Enviar status do jogo via OSC
        enviar_status_jogo_osc()
        
        return jsonify({
            "avancar": False,
            "status": "finalizada",
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "vencedor": {
                "id": vencedor["id"],
                "nome": vencedor["nome"],
                "pontuacao": vencedor["pontuacao"]
            } if vencedor else None,
            "ranking_final": [
                {
                    "posicao": i+1,
                    "id": j["id"],
                    "nome": j["nome"],
                    "pontuacao": j["pontuacao"]
                } for i, j in enumerate(ranking_final)
            ]
        })
    
    # Verificar se todos responderam mas o trigger não ativou
    total_respostas = len(partida.get("respostas_recebidas", set()))
    total_jogadores = len(partida["participantes"])
    todos_responderam = total_respostas >= total_jogadores
    
    if todos_responderam and partida["status"] == "rodada_ativa":
        # Se todos responderam mas o trigger não foi enviado, enviar agora
        enviar_trigger_finaliza_rodada_osc()
        
        return jsonify({
            "avancar": True,
            "status": partida["status"],
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "total_respostas": total_respostas,
            "total_jogadores": total_jogadores,
            "todos_responderam": todos_responderam
        })
    
    return jsonify({
        "avancar": False,
        "status": partida["status"],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "total_respostas": total_respostas,
        "total_jogadores": total_jogadores,
        "todos_responderam": todos_responderam
    })

@app.route('/api/modo_apresentacao', methods=['POST'])
def modo_apresentacao():
    """
    Configura o modo de apresentação (idle) exibindo o ranking dos melhores jogadores.
    Este é o estado inicial do jogo, antes de iniciar uma nova partida.
    """
    global modo_atual, status_jogo
    
    try:
        app.logger.info("Entrando no modo de apresentação")
        
        # Configurar modo de apresentação
        modo_atual = "apresentacao"
        status_jogo = "apresentacao"
        
        # Obter os 3 melhores jogadores (pelo total de pontuação acumulada)
        top_jogadores = sorted(
            jogadores_cadastrados,
            key=lambda x: x["pontuacao_total"],
            reverse=True
        )[:3]
        
        # Pasta para salvar as fotos dos jogadores
        pasta_ranking = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ranking")
        
        # Garantir que a pasta existe
        os.makedirs(pasta_ranking, exist_ok=True)
        
        # Salvar as fotos dos jogadores com nomes padronizados (01.jpg, 02.jpg, 03.jpg)
        for i, jogador in enumerate(top_jogadores):
            if "foto" in jogador and jogador["foto"]:
                try:
                    # Baixar a imagem do jogador
                    response = requests.get(jogador["foto"], stream=True)
                    if response.status_code == 200:
                        # Nome do arquivo (01.jpg, 02.jpg, 03.jpg)
                        nome_arquivo = f"{i+1:02d}.jpg"
                        caminho_arquivo = os.path.join(pasta_ranking, nome_arquivo)
                        
                        # Salvar a imagem
                        with open(caminho_arquivo, 'wb') as arquivo:
                            for chunk in response.iter_content(1024):
                                arquivo.write(chunk)
                        
                        app.logger.info(f"Foto do jogador {jogador['nome']} salva como {nome_arquivo} em {pasta_ranking}")
                    else:
                        app.logger.error(f"Erro ao baixar foto do jogador {jogador['nome']}: status {response.status_code}")
                except Exception as e:
                    app.logger.error(f"Erro ao processar foto do jogador {jogador['nome']}: {str(e)}")
        
        # Logging dos top jogadores
        app.logger.info("Top 3 jogadores do ranking:")
        for i, jogador in enumerate(top_jogadores):
            app.logger.info(f"{i+1}º - {jogador['nome']}: {jogador['pontuacao_total']} pontos")
        
        # Enviar status via OSC
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        return jsonify({
            "status": "ok",
            "modo": "apresentacao",
            "top_jogadores": top_jogadores
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao entrar no modo de apresentação: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao entrar no modo de apresentação: {str(e)}"
        }), 500

def enviar_top_jogadores_osc(jogadores):
    """
    Envia informações dos top jogadores para o Chataigne via OSC.
    """
    try:
        # Informar quantos jogadores estão sendo enviados
        total = len(jogadores)
        osc_client.send_message("/quiz/top/total", total)
        app.logger.info(f"OSC enviado: /quiz/top/total = {total}")
        
        # Enviar ranking como JSON
        osc_client.send_message("/quiz/top/ranking", json.dumps([
            {
                "id": jogador["id"],
                "nome": jogador["nome"],
                "pontuacao": jogador["pontuacao_total"],
                "posicao": i + 1,
                "foto": jogador.get("foto", "")
            } for i, jogador in enumerate(jogadores)
        ]))
        
        # Enviar informações individuais dos jogadores
        for i, jogador in enumerate(jogadores):
            posicao = i + 1
            osc_client.send_message(f"/quiz/top/jogador{posicao}/nome", jogador["nome"])
            osc_client.send_message(f"/quiz/top/jogador{posicao}/pontos", jogador["pontuacao_total"])
            osc_client.send_message(f"/quiz/top/jogador{posicao}/id", jogador["id"])
            if "foto" in jogador:
                osc_client.send_message(f"/quiz/top/jogador{posicao}/foto", jogador["foto"])
            
            app.logger.info(f"OSC enviado: Dados do top jogador {posicao} ({jogador['nome']})")
        
        app.logger.info("Dados dos top jogadores enviados via OSC")
    
    except Exception as e:
        app.logger.error(f"Erro ao enviar top jogadores via OSC: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

def enviar_resposta_osc(dados_resposta):
    """Envia informações da resposta de um jogador para o Chataigne via OSC"""
    try:
        base_address = "/quiz/resposta"
        osc_client.send_message(f"{base_address}/jogador_id", dados_resposta["jogador_id"])
        osc_client.send_message(f"{base_address}/jogador_nome", dados_resposta["jogador_nome"])
        osc_client.send_message(f"{base_address}/correta", 1 if dados_resposta["correta"] else 0)
        osc_client.send_message(f"{base_address}/pontos", dados_resposta["pontos_obtidos"])
        
        # Enviar mensagem específica para cada jogador para acender luz
        jogador_posicao = dados_resposta["jogador_posicao"]
        resultado = 1 if dados_resposta["correta"] else 0
        osc_client.send_message(f"/quiz/jogador{jogador_posicao}", resultado)
        app.logger.info(f"OSC enviado: /quiz/jogador{jogador_posicao} = {resultado} (1=acerto, 0=erro)")
        
        app.logger.info("Resposta do jogador enviada via OSC para o Chataigne")
    except Exception as e:
        app.logger.error(f"Erro ao enviar mensagem OSC de resposta: {str(e)}")

def enviar_final_osc(vencedor, ranking):
    """Envia informações do final do jogo para o Chataigne via OSC"""
    try:
        osc_client.send_message("/quiz/final/vencedor/nome", vencedor["nome"])
        osc_client.send_message("/quiz/final/vencedor/pontos", vencedor["pontuacao"])
        
        # Enviar o ranking final (top 3)
        top3 = ranking[:3]
        for i, jogador in enumerate(top3, 1):
            base_address = f"/quiz/final/ranking{i}"
            osc_client.send_message(f"{base_address}/nome", jogador["nome"])
            osc_client.send_message(f"{base_address}/pontos", jogador["pontuacao"])
        
        app.logger.info("Resultado final enviado via OSC para o Chataigne")
    except Exception as e:
        app.logger.error(f"Erro ao enviar mensagem OSC de final: {str(e)}")

def enviar_status_jogo_osc():
    """
    Envia o status atual do jogo via OSC para o Chataigne
    """
    try:
        # Enviar o status atual
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        # Se estiver em uma partida ativa, enviar informações adicionais
        if status_jogo in ["jogando", "rodada_ativa", "rodada_finalizada", "vinheta_rodada", "abertura_programa"]:
            # Enviar o número da rodada atual e o total de rodadas
            osc_client.send_message("/quiz/rodada/atual", partida["rodada_atual"])
            osc_client.send_message("/quiz/rodada/total", partida["total_rodadas"])
            app.logger.info(f"OSC enviado: Rodada {partida['rodada_atual']}/{partida['total_rodadas']}")
            
            # Enviar pontuações atuais para estados onde isso é relevante
            if status_jogo in ["jogando", "rodada_ativa", "rodada_finalizada"]:
                app.logger.info(f"OSC enviado: Pontuações da partida atual")
                enviar_pontuacoes_atuais_osc()
        
    except Exception as e:
        app.logger.error(f"Erro ao enviar status OSC: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

# Função para atualizar as pontuações totais dos jogadores no banco de dados
def atualizar_pontuacoes_finais():
    """
    Atualiza as pontuações totais dos jogadores no banco de dados
    após o término da partida.
    """
    global jogadores_cadastrados
    
    if not partida["participantes"]:
        return False
    
    app.logger.info("Atualizando pontuações totais dos jogadores no banco de dados...")
    
    # Para cada participante, procurar no banco e somar a pontuação da partida
    for participante in partida["participantes"]:
        jogador_id = participante["id"]
        pontuacao_partida = participante["pontuacao"]
        
        # Procurar o jogador no banco
        for jogador in jogadores_cadastrados:
            if jogador["id"] == jogador_id:
                pontuacao_anterior = jogador["pontuacao_total"]
                jogador["pontuacao_total"] += pontuacao_partida
                jogador["partidas_jogadas"] += 1
                
                # Se foi o vencedor, incrementar as vitórias
                if participante == max(partida["participantes"], key=lambda x: x["pontuacao"]):
                    jogador["vitorias"] += 1
                
                app.logger.info(f"Jogador {jogador['nome']}: {pontuacao_anterior} + {pontuacao_partida} = {jogador['pontuacao_total']} pontos")
                break
    
    return True

# Adicionar novo endpoint para modo de seleção
@app.route('/api/modo_selecao', methods=['POST'])
def modo_selecao():
    """
    Ativa o modo de seleção para configurar uma nova partida.
    """
    global modo_atual, status_jogo
    modo_atual = "selecao"
    status_jogo = "selecao"
    
    # Enviar status do jogo via OSC
    enviar_status_jogo_osc()
    
    return jsonify({
        "status": "ok",
        "modo": modo_atual,
        "jogadores_disponiveis": len(jogadores_cadastrados),
        "jogadores": [
            {
                "id": jogador["id"],
                "nome": jogador["nome"],
                "pontuacao_total": jogador["pontuacao_total"],
                "partidas": jogador["partidas_jogadas"],
                "vitorias": jogador["vitorias"]
            } for jogador in jogadores_cadastrados
        ]
    })

# Modificar o endpoint para configurar partida
@app.route('/api/configurar_partida', methods=['POST'])
def configurar_partida():
    """
    Configura uma nova partida com os jogadores selecionados.
    """
    global modo_atual, status_jogo
    
    # Verificar se está no modo de seleção
    if modo_atual != "selecao":
        return jsonify({
            "status": "erro",
            "erro": "Não é possível configurar uma partida agora",
            "modo_atual": modo_atual
        }), 400
    
    try:
        # Obter dados da configuração
        dados = {}
        if request.is_json:
            dados = request.json
        elif request.form:
            dados = request.form.to_dict()
        
        app.logger.info(f"Dados de configuração recebidos: {dados}")
        
        # Extrair parâmetros
        jogadores_selecionados = dados.get('jogadores_selecionados') or dados.get('jogadores')
        if isinstance(jogadores_selecionados, str):
            # Tentar converter de string JSON para lista
            try:
                import json
                jogadores_selecionados = json.loads(jogadores_selecionados)
            except:
                # Se falhar, tentar dividir por vírgulas
                jogadores_selecionados = [int(id.strip()) for id in jogadores_selecionados.split(',') if id.strip().isdigit()]
        
        duracao_rodada = int(dados.get('duracao_rodada', 30))
        total_rodadas = int(dados.get('total_rodadas', 4))
        tema = dados.get('tema', 'default')
        
        # Validar parâmetros
        if not jogadores_selecionados or len(jogadores_selecionados) != 3:
            return jsonify({
                "status": "erro",
                "erro": "É necessário selecionar exatamente 3 jogadores"
            }), 400
        
        if duracao_rodada <= 0 or total_rodadas <= 0:
            return jsonify({
                "status": "erro",
                "erro": "Duração e total de rodadas precisam ser valores positivos"
            }), 400
        
        # Encontrar os jogadores selecionados
        participantes = []
        for jogador_id in jogadores_selecionados:
            for jogador in jogadores_cadastrados:
                if jogador["id"] == int(jogador_id):
                    # Adicionar uma cópia do jogador com pontuação inicial zerada para a partida
                    participante = {
                        "id": jogador["id"],
                        "nome": jogador["nome"],
                        "foto": jogador["foto"],
                        "pontuacao": 0  # Pontuação zerada para a partida atual
                    }
                    participantes.append(participante)
                    break
        
        # Verificar se todos os jogadores foram encontrados
        if len(participantes) != 3:
            return jsonify({
                "status": "erro",
                "erro": "Nem todos os jogadores selecionados foram encontrados"
            }), 400
        
        # Selecionar perguntas aleatórias
        perguntas_disponiveis = todas_perguntas.copy()
        random.shuffle(perguntas_disponiveis)
        perguntas_selecionadas = perguntas_disponiveis[:total_rodadas]
        
        # Atualizar configuração da partida
        partida["status"] = "preparacao"
        partida["participantes"] = participantes
        partida["rodada_atual"] = 0
        partida["total_rodadas"] = total_rodadas
        partida["duracao_rodada"] = duracao_rodada
        partida["tema"] = tema
        partida["perguntas_selecionadas"] = perguntas_selecionadas
        partida["respostas_recebidas"] = set()
        partida["respostas"] = {}
        partida["avancar_rodada"] = False
        
        # Atualizar modo
        modo_atual = "preparacao"
        status_jogo = "preparacao"
        
        # Enviar status do jogo via OSC
        enviar_status_jogo_osc()
        
        # Enviar informações dos jogadores selecionados via OSC
        enviar_jogadores_partida_osc()
        
        return jsonify({
            "status": "ok",
            "configuracao": {
                "participantes": [p["nome"] for p in participantes],
                "duracao_rodada": duracao_rodada,
                "total_rodadas": total_rodadas,
                "tema": tema
            }
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao configurar partida: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao configurar partida: {str(e)}"
        }), 500

# Inicializa alguns jogadores para testes
def inicializar_jogadores_teste():
    global jogadores_cadastrados
    
    # Limpa a lista de jogadores
    jogadores_cadastrados = []
    
    # Lista de nomes para jogadores
    nomes = [
        "Felipe Brito", "Maria Silva", "João Santos", "Ana Costa", "Pedro Oliveira",
        "Mariana Alves", "Carlos Pereira", "Juliana Martins", "Lucas Ferreira", "Beatriz Campos",
        "André Oliveira", "Camila Souza", "Roberto Almeida", "Fernanda Lima", "Daniel Rodrigues",
        "Amanda Cardoso", "Marcelo Ribeiro", "Patrícia Gomes", "Rodrigo Mendes", "Larissa Dias",
        "Ricardo Barbosa", "Gabriela Ferreira", "Bruno Carvalho", "Carolina Santos", "Gustavo Lima",
        "Vanessa Oliveira", "Alexandre Ramos", "Luciana Vieira", "Fábio Pereira", "Natália Sousa"
    ]
    
    # Dar 860 pontos ao Felipe Brito
    jogador_id = 1
    jogadores_cadastrados.append({
        "id": jogador_id,
        "nome": nomes[0],
        "foto": f"https://randomuser.me/api/portraits/men/{jogador_id}.jpg",
        "telefone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        "pontuacao_total": 860,
        "partidas_jogadas": random.randint(5, 20),
        "vitorias": random.randint(1, 5)
    })
    
    # Adicionar os demais jogadores com pontuações aleatórias
    for i, nome in enumerate(nomes[1:], 2):
        pontuacao = random.randint(50, 800)
        partidas = random.randint(3, 15)
        vitorias = random.randint(0, partidas)
        
        # Usa fotos diferentes para homens e mulheres
        genero = "men" if i % 2 == 0 else "women"
        foto_id = random.randint(1, 99)
        
        jogadores_cadastrados.append({
            "id": i,
            "nome": nome,
            "foto": f"https://randomuser.me/api/portraits/{genero}/{foto_id}.jpg",
            "telefone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            "pontuacao_total": pontuacao,
            "partidas_jogadas": partidas,
            "vitorias": vitorias
        })
    
    app.logger.info(f"Inicializados {len(jogadores_cadastrados)} jogadores para teste")

# Inicializa dados de teste
inicializar_jogadores_teste()

# Modificar o endpoint para iniciar partida
@app.route('/api/iniciar_partida', methods=['POST'])
def iniciar_partida():
    """
    Inicia a partida configurada.
    """
    global modo_atual, status_jogo, partida_db_id
    
    # Verificar se há uma partida configurada
    if not partida["participantes"]:
        return jsonify({
            "status": "erro",
            "erro": "Não há partida configurada para iniciar"
        }), 400
    
    # Atualizar variáveis globais
    modo_atual = "ativo"
    status_jogo = "abertura"  # Corrigido para começar no status "abertura"
    partida["status"] = "abertura"
    
    app.logger.info(f"Iniciando partida com {len(partida['participantes'])} jogadores")
    
    try:
        # Registrar a partida no banco de dados
        partida_db_id = registrar_partida(
            partida["participantes"],
            partida["total_rodadas"],
            partida["duracao_rodada"]
        )
        
        # Atualizar o status da partida no banco de dados
        if partida_db_id:
            atualizar_status_partida(partida_db_id, 'jogando')
            app.logger.info(f"Partida registrada no banco de dados com ID: {partida_db_id}")
    except Exception as e:
        app.logger.error(f"Erro ao registrar a partida no banco de dados: {str(e)}")
    
    # Enviar status do jogo via OSC
    enviar_status_jogo_osc()
    
    # Retornar resposta
    return jsonify({
        "status": "ok",
        "mensagem": "Partida iniciada com sucesso",
        "participantes": [
            {
                "id": jogador["id"],
                "nome": jogador["nome"],
                "pontuacao": jogador["pontuacao"]
            } for jogador in partida["participantes"]
        ],
        "rodada_atual": partida["rodada_atual"],
        "total_rodadas": partida["total_rodadas"],
        "status_jogo": status_jogo
    })

@app.route('/api/iniciar_rodada', methods=['POST'])
def iniciar_rodada():
    """
    Endpoint para iniciar uma nova rodada com a pergunta.
    Este é o estado que segue após a vinheta da rodada terminar.
    """
    global partida, status_jogo
    
    try:
        app.logger.info("Solicitação para iniciar nova rodada")
        
        # Verificar estado do jogo
        estados_validos = ["aguardando_rodada", "rodada_finalizada", "jogando", "vinheta_rodada", "abertura_programa"]
        if partida["status"] not in estados_validos:
            return jsonify({
                "status": "erro",
                "erro": "Não é possível iniciar uma rodada agora",
                "status_atual": partida["status"]
            }), 400
        
        # Se estiver vindo da vinheta_rodada, já temos o rodada_atual incrementado
        # Caso contrário, incrementamos aqui
        if partida["status"] != "vinheta_rodada":
            # Incrementar rodada atual
            partida["rodada_atual"] += 1
        
        # Log para debug
        app.logger.info(f"Iniciando rodada {partida['rodada_atual']} de {partida['total_rodadas']}")
        
        # Verificar se já passamos do total de rodadas
        if partida["rodada_atual"] > partida["total_rodadas"]:
            # Finalizar o jogo
            return finalizar_jogo()
        
        # Obter a pergunta para esta rodada
        index_pergunta = partida["rodada_atual"] - 1
        if index_pergunta >= len(partida["perguntas_selecionadas"]):
            app.logger.error(f"Índice de pergunta inválido: {index_pergunta}")
            return jsonify({
                "status": "erro",
                "erro": "Pergunta não encontrada para esta rodada"
            }), 400
        
        pergunta_atual = partida["perguntas_selecionadas"][index_pergunta]
        
        # Limitar a apenas 3 opções (A, B, C)
        if len(pergunta_atual["opcoes"]) > 3:
            # Se a resposta certa está além das 3 primeiras opções, troque-a com uma das 3 primeiras
            if pergunta_atual["resposta_correta"] > 3:
                # Salvar a opção correta
                opcao_correta = pergunta_atual["opcoes"][pergunta_atual["resposta_correta"] - 1]
                # Escolher aleatoriamente uma posição entre 1-3 para colocar a resposta correta
                nova_posicao = random.randint(1, 3)
                # Trocar a opção correta com uma das 3 primeiras
                pergunta_atual["opcoes"][pergunta_atual["resposta_correta"] - 1] = pergunta_atual["opcoes"][nova_posicao - 1]
                pergunta_atual["opcoes"][nova_posicao - 1] = opcao_correta
                # Atualizar a posição da resposta correta
                pergunta_atual["resposta_correta"] = nova_posicao
            
            # Manter apenas 3 opções
            pergunta_atual["opcoes"] = pergunta_atual["opcoes"][:3]
            
            # Garantir que resposta_correta esteja entre 1-3
            if pergunta_atual["resposta_correta"] > 3:
                pergunta_atual["resposta_correta"] = random.randint(1, 3)
        
        # Adicionar a pergunta atual ao estado da partida
        partida["pergunta_atual"] = pergunta_atual
        
        # Iniciar a rodada
        partida["status"] = "rodada_ativa"
        partida["inicio_rodada"] = time.time()
        partida["fim_rodada"] = partida["inicio_rodada"] + partida["duracao_rodada"]
        partida["respostas_recebidas"] = set()
        partida["respostas"] = {}
        partida["avancar_rodada"] = False
        
        # Atualizar status do jogo
        status_jogo = "jogando"
        
        # Enviar status via OSC diretamente
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        # Enviar informações adicionais
        osc_client.send_message("/quiz/rodada/atual", partida["rodada_atual"])
        osc_client.send_message("/quiz/rodada/total", partida["total_rodadas"])
        
        # Enviar a pergunta atual via OSC
        osc_client.send_message("/quiz/pergunta/texto", pergunta_atual["pergunta"])
        
        # Enviar cada opção separadamente
        for i, opcao in enumerate(pergunta_atual["opcoes"]):
            osc_client.send_message(f"/quiz/pergunta/opcao{i+1}", opcao)
        
        # Ainda enviar todas as opções juntas para compatibilidade
        osc_client.send_message("/quiz/pergunta/opcoes", json.dumps(pergunta_atual["opcoes"]))
        
        # Enviar a resposta correta
        osc_client.send_message("/quiz/pergunta/resposta_correta", pergunta_atual["resposta_correta"])
        app.logger.info(f"OSC enviado: Pergunta da rodada {partida['rodada_atual']}")
        
        # Enviar pontuações atuais
        enviar_pontuacoes_atuais_osc()
        
        # Iniciar um temporizador para finalizar a rodada automaticamente
        def finalizar_rodada_automaticamente():
            # Espera o tempo da rodada
            time.sleep(partida["duracao_rodada"])
            
            # Verifica se a rodada ainda está ativa (pode ter sido finalizada manualmente)
            if partida["status"] == "rodada_ativa":
                app.logger.info("Tempo da rodada esgotado! Finalizando automaticamente...")
                
                # Registrar como erro para os jogadores que não responderam
                for p in partida["participantes"]:
                    jogador_id = str(p["id"])
                    
                    # Se o jogador ainda não respondeu
                    if jogador_id not in partida.get("respostas_recebidas", set()):
                        app.logger.info(f"Jogador {p['nome']} não respondeu dentro do tempo!")
                        
                        # Enviar sinal OSC de erro para o jogador
                        for i, participante in enumerate(partida["participantes"]):
                            if participante["id"] == p["id"]:
                                posicao = i + 1
                                osc_client.send_message(f"/quiz/jogador{posicao}", 0)
                                app.logger.info(f"OSC enviado: /quiz/jogador{posicao} = 0 (tempo esgotado)")
                                break
                        
                        # Registrar resposta com pontuação zero
                        if "respostas" not in partida:
                            partida["respostas"] = {}
                        
                        # Adicionar à lista de respostas recebidas
                        if "respostas_recebidas" not in partida:
                            partida["respostas_recebidas"] = set()
                        
                        partida["respostas_recebidas"].add(jogador_id)
                        
                        # Registrar resposta com pontuação zero
                        partida["respostas"][jogador_id] = {
                            "resposta": None,
                            "tempo": partida["duracao_rodada"] * 1000,  # Em milissegundos
                            "correta": False,
                            "pontos": 0,
                            "tempo_esgotado": True
                        }
                
                # Finalizar a rodada
                partida["avancar_rodada"] = True
                status_jogo = "rodada_finalizada"
                
                # Enviar trigger OSC para finalizar a rodada
                enviar_trigger_finaliza_rodada_osc()
                
                # Enviar status atualizado
                enviar_status_jogo_osc()
        
        # Iniciar o temporizador em uma thread separada
        timer_thread = threading.Thread(target=finalizar_rodada_automaticamente)
        timer_thread.daemon = True  # Thread em segundo plano
        timer_thread.start()
        
        # Devolver dados da rodada
        return jsonify({
            "status": "ok",
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "duracao_rodada": partida["duracao_rodada"],
            "pergunta": pergunta_atual["pergunta"],
            "opcoes": pergunta_atual["opcoes"],
            "status_jogo": status_jogo
        })
    
    except Exception as e:
        app.logger.error(f"Erro ao iniciar rodada: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao iniciar rodada: {str(e)}"
        }), 500

@app.route('/api/vinheta_rodada', methods=['POST'])
def vinheta_rodada():
    """
    Endpoint para indicar que a vinheta da rodada está sendo exibida.
    Este é um estado intermediário entre a abertura do programa e o início efetivo 
    da rodada com a pergunta.
    """
    global status_jogo, partida
    
    try:
        # Obter dados da requisição (opcional, para informações adicionais)
        dados = {}
        if request.is_json:
            dados = request.json
        elif request.form:
            dados = request.form.to_dict()
        elif request.args:
            dados = request.args.to_dict()
            
        app.logger.info(f"Vinheta da rodada em exibição: {dados}")
        
        # Calcular próxima rodada
        rodada_atual = partida["rodada_atual"] + 1 if partida["rodada_atual"] < partida["total_rodadas"] else partida["rodada_atual"]
        
        # Atualizar o número da rodada atual
        partida["rodada_atual"] = rodada_atual
        
        # Atualizar o status para vinheta rodada #
        status_jogo = f"vinheta rodada {rodada_atual}"
        partida["status"] = "vinheta_rodada"
        
        # Enviar status via OSC
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        # Enviar informações sobre a rodada
        osc_client.send_message("/quiz/rodada/atual", rodada_atual)
        osc_client.send_message("/quiz/rodada/total", partida["total_rodadas"])
        app.logger.info(f"OSC enviado: Vinheta da rodada {rodada_atual}/{partida['total_rodadas']}")
        
        return jsonify({
            "status": "ok",
            "mensagem": f"Vinheta da rodada {rodada_atual} em exibição",
            "rodada_atual": rodada_atual,
            "total_rodadas": partida["total_rodadas"],
            "status_jogo": status_jogo
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar vinheta: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao processar vinheta: {str(e)}"
        }), 500

def finalizar_jogo():
    """
    Finaliza o jogo e atualiza as pontuações totais dos jogadores no ranking.
    """
    global status_jogo
    
    try:
        # Atualizar status da partida
        partida["status"] = "finalizada"
        status_jogo = "jogo_finalizado"
        
        # Atualizar pontuações totais dos jogadores
        atualizar_pontuacoes_finais()
        
        # Determinar o vencedor
        vencedor = max(partida["participantes"], key=lambda x: x["pontuacao"])
        app.logger.info(f"Jogo finalizado! Vencedor: {vencedor['nome']} com {vencedor['pontuacao']} pontos")
        
        # Enviar status via OSC
        enviar_status_jogo_osc()
        
        # Enviar informações do vencedor via OSC
        osc_client.send_message("/quiz/final/vencedor/nome", vencedor["nome"])
        osc_client.send_message("/quiz/final/vencedor/pontos", vencedor["pontuacao"])
        
        # Enviar ranking final via OSC
        participantes_ordenados = sorted(partida["participantes"], key=lambda x: x["pontuacao"], reverse=True)
        for i, jogador in enumerate(participantes_ordenados, 1):
            osc_client.send_message(f"/quiz/final/ranking/{i}/nome", jogador["nome"])
            osc_client.send_message(f"/quiz/final/ranking/{i}/pontos", jogador["pontuacao"])
            osc_client.send_message(f"/quiz/final/ranking/{i}/posicao", i)
        
        return jsonify({
            "status": "ok",
            "mensagem": "Jogo finalizado!",
            "vencedor": {
                "nome": vencedor["nome"],
                "pontuacao": vencedor["pontuacao"]
            },
            "ranking": [
                {
                    "nome": p["nome"],
                    "pontuacao": p["pontuacao"],
                    "posicao": i+1
                } for i, p in enumerate(participantes_ordenados)
            ]
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao finalizar jogo: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao finalizar jogo: {str(e)}"
        }), 500

@app.route('/api/avancar_rodada', methods=['POST'])
def avancar_rodada():
    """
    Endpoint para avançar para a próxima rodada após uma rodada ser finalizada.
    Este endpoint deve ser chamado pelo Chataigne após a animação de finalização da rodada.
    """
    global status_jogo
    
    try:
        app.logger.info("Solicitação para avançar para a próxima rodada")
        
        # Verificar se estamos em estado que permite avançar
        if partida["status"] not in ["aguardando_rodada", "rodada_finalizada"]:
            return jsonify({
                "status": "erro",
                "erro": "Não é possível avançar para a próxima rodada neste momento",
                "status_atual": partida["status"]
            }), 400
        
        # Verificar se já terminamos todas as rodadas
        if partida["rodada_atual"] >= partida["total_rodadas"]:
            # Finalizar o jogo
            return finalizar_jogo()
        
        # Limpar as respostas da rodada anterior
        partida["respostas_recebidas"] = set()
        partida["respostas"] = {}
        partida["avancar_rodada"] = False
        
        # Mudar o status para aguardando vinheta
        status_jogo = "aguardando_vinheta"
        
        # Enviar status via OSC
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        # Enviar sinal para exibir a vinheta da próxima rodada
        proxima_rodada = partida["rodada_atual"] + 1
        osc_client.send_message("/quiz/rodada/proxima", proxima_rodada)
        app.logger.info(f"OSC enviado: Próxima rodada = {proxima_rodada}")
        
        return jsonify({
            "status": "ok",
            "mensagem": f"Avançando para a rodada {proxima_rodada}",
            "rodada_atual": partida["rodada_atual"],
            "proxima_rodada": proxima_rodada,
            "total_rodadas": partida["total_rodadas"],
            "status_jogo": status_jogo
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao avançar rodada: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao avançar rodada: {str(e)}"
        }), 500

@app.route('/api/status_rodada', methods=['GET'])
def status_rodada():
    """
    Retorna detalhes sobre o status da rodada atual
    """
    try:
        # Verificar se existe uma rodada ativa
        if partida.get("status") != "rodada_ativa":
            return jsonify({
                "status": "erro",
                "erro": "Não há uma rodada ativa no momento",
                "status_atual": partida.get("status")
            }), 400
            
        # Calcular o tempo restante
        tempo_decorrido = time.time() - partida.get("tempo_inicio", 0)
        tempo_total = partida.get("duracao_rodada", 30)
        tempo_restante = max(0, tempo_total - tempo_decorrido)
        
        # Obter respostas recebidas
        respostas_recebidas = list(partida.get("respostas_recebidas", set()))
        
        # Verificar quais jogadores já responderam
        jogadores_responderam = []
        for i, jogador in enumerate(partida.get("participantes", [])):
            jogador_id = str(jogador["id"])
            respondeu = jogador_id in respostas_recebidas
            jogadores_responderam.append({
                "posicao": i + 1,
                "id": jogador,
                "nome": obter_nome_jogador(jogador_id),
                "respondeu": respondeu,
                "resposta": partida.get("respostas", {}).get(jogador_id, None) if respondeu else None
            })
            
        resultado = {
            "status": "ok",
            "rodada_atual": partida.get("rodada_atual", 0),
            "total_rodadas": partida.get("total_rodadas", 0),
            "pergunta": partida.get("pergunta_atual", {}).get("pergunta", ""),
            "opcoes": partida.get("pergunta_atual", {}).get("opcoes", []),
            "resposta_correta": partida.get("pergunta_atual", {}).get("resposta_correta", 0),
            "tempo_restante": tempo_restante,
            "tempo_total": tempo_total,
            "jogadores": jogadores_responderam,
            "total_respostas": len(respostas_recebidas),
            "total_jogadores": len(partida.get("participantes", [])),
            "todos_responderam": len(respostas_recebidas) >= len(partida.get("participantes", [])),
            "status_jogo": status_jogo
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        app.logger.error(f"Erro ao obter status da rodada: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao obter status da rodada: {str(e)}"
        }), 500

# Funções auxiliares
def obter_nome_jogador(jogador_id):
    """Obtém o nome de um jogador pelo seu ID"""
    # Primeiro verificar nos participantes da partida atual
    for jogador in partida.get("participantes", []):
        if str(jogador["id"]) == str(jogador_id):
            return jogador["nome"]
    
    # Se não encontrar, procurar na lista de jogadores cadastrados
    for jogador in jogadores_cadastrados:
        if str(jogador["id"]) == str(jogador_id):
            return jogador["nome"]
    
    return None

def calcular_ranking_atual():
    """Calcula o ranking atual dos jogadores na partida"""
    if not partida.get("participantes"):
        return []
        
    # Ordenar participantes por pontuação (maior para menor)
    ranking = sorted(
        partida["participantes"], 
        key=lambda x: x["pontuacao"], 
        reverse=True
    )
    
    # Adicionar posição ao ranking
    for i, jogador in enumerate(ranking):
        jogador["posicao"] = i + 1
        
    return ranking

# Variável para controlar se já inicializamos o DB
db_initialized = False

@app.before_request
def before_request():
    """Inicializa o banco de dados na primeira requisição"""
    global db_initialized
    if not db_initialized:
        init_db()
        app.logger.info("Banco de dados inicializado para a aplicação")
        db_initialized = True

# Adicionar endpoint para finalizar rodada (apenas para compatibilidade com Chataigne)
@app.route('/api/finalizar_rodada', methods=['POST'])
def finalizar_rodada_http():
    """Endpoint para confirmar a finalização de uma rodada via HTTP.
    Este endpoint existe principalmente por compatibilidade com o Chataigne.
    A finalização da rodada já é tratada automaticamente pelo backend quando todos respondem
    ou o tempo acaba, e um trigger OSC é enviado."""
    
    global status_jogo
    
    try:
        app.logger.info("Recebida solicitação para finalizar rodada via HTTP")
        
        # Verificar se a rodada já está finalizada
        if partida["status"] != "aguardando_rodada" or status_jogo != "rodada_finalizada":
            # Se a rodada ainda não estiver finalizada, finalizá-la
            status_jogo = "rodada_finalizada"
            partida["status"] = "aguardando_rodada"
            
            # Enviar todos os sinais necessários via OSC
            enviar_trigger_finaliza_rodada_osc()
        
        # Retornar o status atual
        return jsonify({
            "status": "ok",
            "mensagem": "Rodada finalizada com sucesso",
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "proximo_passo": "Chamar /api/vinheta_rodada para iniciar a próxima rodada"
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao finalizar rodada via HTTP: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"status": "erro", "erro": f"Erro ao finalizar rodada: {str(e)}"}), 500

@app.route('/api/nova_partida', methods=['POST'])
def nova_partida():
    """
    Cria uma nova partida, resetando o estado do jogo.
    Este endpoint deve ser chamado antes de configurar uma nova partida.
    """
    global partida, status_jogo, partida_db_id
    
    try:
        app.logger.info("Iniciando nova partida")
        
        # Reset do estado da partida
        partida = {
            "status": "aguardando",
            "participantes": [],
            "rodada_atual": 0,
            "total_rodadas": 0,
            "duracao_rodada": 30.0,
            "perguntas_selecionadas": [],
            "pergunta_atual": None,
            "respostas_recebidas": set(),
            "respostas": {},
            "inicio_rodada": 0,
            "fim_rodada": 0,
            "avancar_rodada": False,
            "tema": "default",
            "participantes_ativos": 0
        }
        
        # Reset do status do jogo
        status_jogo = "aguardando"
        
        # Reset do ID da partida no banco de dados
        partida_db_id = None
        
        # Enviar status atualizado via OSC
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        return jsonify({
            "status": "ok",
            "mensagem": "Nova partida iniciada com sucesso",
            "status_jogo": status_jogo
        })
    
    except Exception as e:
        app.logger.error(f"Erro ao iniciar nova partida: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao iniciar nova partida: {str(e)}"
        }), 500

def enviar_jogadores_partida_osc():
    """
    Envia informações dos jogadores da partida atual via OSC.
    """
    global partida
    
    if not partida or not partida.get("participantes"):
        app.logger.warning("Não há participantes para enviar via OSC")
        return
    
    try:
        # Enviar total de jogadores
        total_jogadores = len(partida["participantes"])
        osc_client.send_message("/quiz/jogadores/total", total_jogadores)
        app.logger.info(f"OSC enviado: /quiz/jogadores/total = {total_jogadores}")
        
        # Enviar informações individuais dos jogadores
        for i, jogador in enumerate(partida["participantes"]):
            posicao = i + 1
            osc_client.send_message(f"/quiz/jogador{posicao}/id", jogador["id"])
            osc_client.send_message(f"/quiz/jogador{posicao}/nome", jogador["nome"])
            osc_client.send_message(f"/quiz/jogador{posicao}/pontos", jogador["pontuacao"])
            osc_client.send_message(f"/quiz/jogador{posicao}/posicao", posicao)
            
            app.logger.info(f"OSC enviado: Dados do jogador {posicao} ({jogador['nome']})")
        
        app.logger.info("Dados de todos os jogadores enviados via OSC")
    
    except Exception as e:
        app.logger.error(f"Erro ao enviar jogadores via OSC: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

def enviar_pontuacoes_atuais_osc():
    """
    Envia as pontuações atuais dos jogadores via OSC para o Chataigne.
    """
    if not partida or not partida.get("participantes"):
        app.logger.warning("Não há participantes para enviar pontuações via OSC")
        return
    
    try:
        # Calcular o ranking atual (ordenado por pontuação)
        ranking = sorted(
            partida["participantes"],
            key=lambda x: x["pontuacao"],
            reverse=True
        )
        
        # Enviar o ranking atual como JSON
        osc_client.send_message("/quiz/ranking", json.dumps([
            {
                "id": p["id"],
                "nome": p["nome"],
                "pontuacao": p["pontuacao"],
                "posicao": i + 1
            } for i, p in enumerate(ranking)
        ]))
        
        # Enviar informações individuais dos jogadores
        for i, jogador in enumerate(ranking):
            posicao = i + 1
            osc_client.send_message(f"/quiz/partida/jogador{posicao}/nome", jogador["nome"])
            osc_client.send_message(f"/quiz/partida/jogador{posicao}/pontos", jogador["pontuacao"])
            osc_client.send_message(f"/quiz/partida/jogador{posicao}/posicao", posicao)
            osc_client.send_message(f"/quiz/partida/jogador{posicao}/id", jogador["id"])
        
        app.logger.info("Pontuações atuais enviadas via OSC")
    
    except Exception as e:
        app.logger.error(f"Erro ao enviar pontuações via OSC: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

def enviar_trigger_finaliza_rodada_osc():
    """
    Envia um sinal de trigger OSC para indicar que a rodada foi finalizada.
    Este sinal é um pulso (1 seguido de 0) enviado para o endereço /quiz/trigger/finaliza_rodada.
    O Chataigne deve reagir a este pulso chamando a próxima etapa no fluxo do jogo.
    """
    global status_jogo, partida
    
    try:
        # Atualizar status do jogo
        status_jogo = "rodada_finalizada"
        partida["status"] = "aguardando_rodada"
        
        # Enviar status atualizado
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        # Enviar informações da rodada finalizada
        osc_client.send_message("/quiz/rodada/atual", partida["rodada_atual"])
        osc_client.send_message("/quiz/rodada/total", partida["total_rodadas"])
        
        # Enviar sinal da resposta correta
        if "pergunta_atual" in partida and partida["pergunta_atual"]:
            osc_client.send_message("/quiz/resposta_correta", partida["pergunta_atual"]["resposta_correta"])
            
        # Enviar ranking atualizado
        ranking = sorted(partida["participantes"], key=lambda x: x["pontuacao"], reverse=True)
        osc_client.send_message("/quiz/ranking", json.dumps([
            {
                "id": p["id"],
                "nome": p["nome"],
                "pontuacao": p["pontuacao"],
                "posicao": i + 1
            } for i, p in enumerate(ranking)
        ]))
        
        # Enviar informação que todos responderam
        osc_client.send_message("/quiz/todos_responderam", 1)
        
        # Enviar o trigger como um pulso (1 seguido de 0 após um breve delay)
        osc_client.send_message("/quiz/trigger/finaliza_rodada", 1)
        app.logger.info("OSC enviado: Trigger de finalização de rodada (1)")
        
        # Criar uma thread para enviar o reset do trigger após um breve delay
        def reset_trigger():
            time.sleep(0.2)  # 200ms de delay para criar um pulso visível
            osc_client.send_message("/quiz/trigger/finaliza_rodada", 0)
            app.logger.info("OSC enviado: Reset do trigger de finalização (0)")
        
        # Iniciar thread para reset do trigger
        reset_thread = threading.Thread(target=reset_trigger)
        reset_thread.daemon = True
        reset_thread.start()
        
    except Exception as e:
        app.logger.error(f"Erro ao enviar trigger de finalização: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())

@app.route('/api/abertura_rodada', methods=['POST'])
def abertura_rodada():
    """
    Exibe a vinheta principal do jogo após iniciar a partida.
    Esta função deve ser chamada após iniciar a partida e antes da primeira rodada.
    """
    global status_jogo, partida
    
    try:
        app.logger.info("Iniciando abertura do programa")
        
        # Verificar se a partida foi iniciada
        if partida["status"] not in ["preparacao", "iniciada", "abertura"]:
            return jsonify({
                "status": "erro",
                "erro": "Não é possível exibir a abertura agora",
                "status_atual": partida["status"]
            }), 400
        
        # Atualizar o status do jogo para abertura
        status_jogo = "abertura_programa"
        partida["status"] = "abertura_programa"
        
        # Enviar status via OSC
        osc_client.send_message("/quiz/status", status_jogo)
        app.logger.info(f"OSC enviado: /quiz/status = {status_jogo}")
        
        # Enviar informações adicionais
        osc_client.send_message("/quiz/rodada/atual", partida["rodada_atual"])
        osc_client.send_message("/quiz/rodada/total", partida["total_rodadas"])
        
        # Enviar informações dos jogadores
        enviar_jogadores_partida_osc()
        
        # Enviar pontuações iniciais
        enviar_pontuacoes_atuais_osc()
        
        return jsonify({
            "status": "ok",
            "mensagem": "Abertura do programa em exibição",
            "rodada_atual": partida["rodada_atual"],
            "total_rodadas": partida["total_rodadas"],
            "status_jogo": status_jogo
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao processar abertura: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "erro",
            "erro": f"Erro ao processar abertura: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
