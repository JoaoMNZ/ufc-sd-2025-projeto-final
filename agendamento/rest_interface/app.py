from flask import Flask, request, jsonify
import xmlrpc.client
import os
import requests
import datetime

app = Flask(__name__)

# Configurações de Conexão
rpc_host = os.getenv('RPC_HOST', 'rpc-service')
rpc_url = f"http://{rpc_host}:8000/RPC2"
notificacao_url = os.getenv('NOTIFICACAO_URL', 'http://notificacoes:5000/enviar')

print(f"[INIT] Conectando ao RPC em: {rpc_url}")
rpc_proxy = xmlrpc.client.ServerProxy(rpc_url)

def enviar_notificacao(evento, agendamento_id, paciente_id, status):
    try:
        msg = {
            "evento": evento,
            "agendamento_id": agendamento_id,
            "paciente_id": paciente_id,
            "status": status,
            "timestamp": str(datetime.datetime.now())
        }
        requests.post(notificacao_url, json=msg, timeout=2)
        print(f"[LOG] Notificacao enviada: {evento}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar notificacao: {e}")

@app.route('/agendar', methods=['POST'])
def agendar():
    dados = request.json
    if not dados:
        return jsonify({"erro": "JSON invalido"}), 400

    medico_id = dados.get('medico_id')
    paciente_id = dados.get('paciente_id')
    data_hora = dados.get('data_hora')
    especialidade = dados.get('especialidade')
    tipo_pagamento = dados.get('tipo_pagamento')
    detalhes_pagamento = dados.get('detalhes_pagamento')

    if not all([medico_id, paciente_id, data_hora, especialidade]):
         return jsonify({"erro": "Faltam dados obrigatorios."}), 400

    try:
        print(f"[LOG] Processando agendamento. Medico: {medico_id}, Data: {data_hora}")
        resposta = rpc_proxy.agendar_consulta(medico_id, paciente_id, data_hora, especialidade, tipo_pagamento, detalhes_pagamento)
        
        if resposta.get('status') == 'sucesso':
            enviar_notificacao("AGENDAMENTO_CRIADO", resposta.get('id_consulta'), paciente_id, "AGUARDANDO_VALIDACAO")

        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": f"Erro RPC: {str(e)}"}), 500

@app.route('/consultas', methods=['GET'])
def listar():
    try:
        resposta = rpc_proxy.listar_consultas()
        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/agendar/<int:id_consulta>', methods=['PUT'])
def atualizar_consulta(id_consulta):
    dados = request.json
    novo_status = dados.get('status')
    
    if not novo_status:
        return jsonify({"erro": "Status obrigatorio"}), 400

    try:
        resposta = rpc_proxy.atualizar_status(id_consulta, novo_status)
        
        if resposta.get('status') == 'sucesso':
            enviar_notificacao(f"AGENDAMENTO_{novo_status.upper()}", id_consulta, 0, novo_status)

        return jsonify(resposta), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)