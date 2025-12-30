from flask import Flask, request, jsonify
import socket
import json
import logging

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("convenio-interface")

# Configuração do serviço backend (Java)
BACKEND_HOST = "convenio-service"
BACKEND_PORT = 5003
SOCKET_TIMEOUT = 10


def enviar_para_backend(mensagem: dict) -> dict:
    """Envia mensagem via socket TCP para o serviço Java"""
    try:
        with socket.create_connection(
                (BACKEND_HOST, BACKEND_PORT),
                timeout=SOCKET_TIMEOUT
        ) as sock:
            # Converte para JSON e adiciona newline
            mensagem_json = json.dumps(mensagem) + '\n'
            sock.sendall(mensagem_json.encode('utf-8'))

            # Recebe resposta (pode ser maior que 1024)
            resposta = sock.recv(4096).decode('utf-8')

            # Converte resposta JSON para dict
            return json.loads(resposta)
    except Exception as e:
        logger.error(f"Erro ao comunicar com backend: {e}")
        return {"success": False, "error": str(e)}


@app.route("/api/convenio/validar", methods=["POST"])
def validar_pagamento():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "error": "JSON inválido"}), 400

    # Validações básicas
    if not data.get("agendamento_id"):
        return jsonify({"success": False, "error": "agendamento_id obrigatório"}), 400

    if not data.get("paciente_id"):
        return jsonify({"success": False, "error": "paciente_id obrigatório"}), 400

    if not data.get("tipo_pagamento"):
        return jsonify({"success": False, "error": "tipo_pagamento obrigatório"}), 400

    tipo_pagamento = data["tipo_pagamento"].upper()

    if tipo_pagamento not in ["CONVENIO", "PARTICULAR"]:
        return jsonify({"success": False, "error": "Tipo de pagamento inválido"}), 400

    # Monta mensagem para o backend
    mensagem = {
        "action": "validar_pagamento",
        "agendamento_id": data["agendamento_id"],
        "paciente_id": data["paciente_id"],
        "tipo_pagamento": tipo_pagamento
    }

    if tipo_pagamento == "CONVENIO":
        if "convenio_nome" not in data:
            return jsonify({"success": False, "error": "convenio_nome é obrigatório"}), 400
        mensagem["convenio_nome"] = data["convenio_nome"]

    if tipo_pagamento == "PARTICULAR":
        # Aceita tanto 'numero_cartao' quanto 'cartao_numero'
        numero_cartao = data.get("numero_cartao") or data.get("cartao_numero")

        if not numero_cartao:
            return jsonify({"success": False, "error": "numero_cartao é obrigatório"}), 400

        # Remove espaços e valida tamanho
        numero_cartao = ''.join(filter(str.isdigit, str(numero_cartao)))

        if len(numero_cartao) < 13 or len(numero_cartao) > 19:
            return jsonify({"success": False, "error": "Número de cartão inválido"}), 400

        mensagem["numero_cartao"] = numero_cartao

    try:
        logger.info(f"Enviando para backend: {mensagem}")
        resposta = enviar_para_backend(mensagem)
        logger.info(f"Resposta do backend: {resposta}")

        # Retorna a resposta do backend diretamente
        status_code = 200 if resposta.get("success") else 400
        return jsonify(resposta), status_code

    except Exception as e:
        logger.error(f"Erro ao comunicar com backend: {e}")
        return jsonify({"success": False, "error": "Falha na comunicação com o serviço"}), 503


@app.route("/health", methods=["GET"])
def healthcheck():
    return jsonify({
        "status": "healthy",
        "service": "convenio-interface",
        "backend": f"{BACKEND_HOST}:{BACKEND_PORT}"
    })


@app.route("/api/convenio/docs", methods=["GET"])
def docs():
    return jsonify({
        "service": "Serviço de Validação de Convênio",
        "version": "1.0",
        "endpoints": [
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check"
            },
            {
                "path": "/api/convenio/validar",
                "method": "POST",
                "description": "Valida pagamento (convênio ou cartão)"
            },
            {
                "path": "/api/convenio/docs",
                "method": "GET",
                "description": "Documentação da API"
            }
        ]
    })


if __name__ == "__main__":
    logger.info("Iniciando Interface REST na porta 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
