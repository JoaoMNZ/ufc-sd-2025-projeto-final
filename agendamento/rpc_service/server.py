from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# MOCK DO BANCO DE DADOS
agendamentos_mock = []
ultimo_id = 0  # contador pra gerar os ids

def verificar_hora_cheia(data_hora):
    # regra do grupo: apenas horas cheias permitidas (terminadas em :00)
    return data_hora.endswith(":00")

def verificar_disponibilidade(medico_id, paciente_id, data_hora):
    for agendamento in agendamentos_mock:
        # ignora se tiver cancelada
        if agendamento['status'] == 'cancelada':
            continue

        if agendamento['data_hora'] == data_hora:
            # regra 1: medico nao pode atender dois ao mesmo tempo
            if agendamento['medico_id'] == medico_id:
                return {"disponivel": False, "mensagem": "Horario indisponivel para este medico."}
            
            # regra 2: paciente nao pode estar em dois lugares ao mesmo tempo
            if agendamento['paciente_id'] == paciente_id:
                return {"disponivel": False, "mensagem": "Paciente ja possui agendamento neste horario."}
                
    return {"disponivel": True}

def agendar_consulta(medico_id, paciente_id, data_hora, especialidade, tipo_pagamento, detalhes_pagamento):
    global ultimo_id
    print(f"[RPC] Novo pedido: Medico {medico_id} | Paciente {paciente_id} | {data_hora}")
    
    # validação de hora cheia
    if not verificar_hora_cheia(data_hora):
        return {"status": "erro", "mensagem": "Apenas horarios cheios sao permitidos (ex: 08:00)."}

    # verificação de conflitos (medico e paciente)
    checa = verificar_disponibilidade(medico_id, paciente_id, data_hora)
    if not checa['disponivel']:
        return {"status": "erro", "mensagem": checa['mensagem']}
    
    # campos pedidos no pdf e pelo grupo
    ultimo_id += 1
    novo_agendamento = {
        "id": ultimo_id,
        "medico_id": medico_id,
        "paciente_id": paciente_id,
        "data_hora": data_hora,
        "especialidade": especialidade,
        "tipo_pagamento": tipo_pagamento,       # novo campo (convenio/particular)
        "detalhes_pagamento": detalhes_pagamento, # cartao ou nome do convenio
        "status": "aguardando_validacao"        # status inicial mudou conforme o fluxo do grupo
    }
    agendamentos_mock.append(novo_agendamento)
    
    return {"status": "sucesso", "mensagem": "Pré-agendamento realizado! Aguardando validação.", "id_consulta": ultimo_id}

def listar_consultas():
    return agendamentos_mock

def atualizar_status(id_consulta, novo_status):
    print(f"[RPC] Atualizando consulta {id_consulta} para {novo_status}")
    
    # procura a consulta pelo id na lista
    for agendamento in agendamentos_mock:
        if agendamento['id'] == id_consulta:
            agendamento['status'] = novo_status
            return {"status": "sucesso", "mensagem": f"Status alterado para {novo_status}"}
    
    return {"status": "erro", "mensagem": "Consulta nao encontrada"}

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

with SimpleXMLRPCServer(('0.0.0.0', 8000), requestHandler=RequestHandler, allow_none=True) as server:
    server.register_introspection_functions()
    server.register_function(agendar_consulta, 'agendar_consulta')
    server.register_function(listar_consultas, 'listar_consultas')
    server.register_function(atualizar_status, 'atualizar_status')
    print("Serviço de Agendamento rodando com regras de negócio...")
    server.serve_forever()