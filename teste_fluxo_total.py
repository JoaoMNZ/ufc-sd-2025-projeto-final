import requests
import time
import sys

# --- CONFIGURAÇÕES ---
URL_USERS = "http://localhost:5001"
URL_AGENDA = "http://localhost:5000"
URL_CONVENIO = "http://localhost:5002"

def log(tag, msg):
    print(f"[{tag}] {msg}")

def teste_completo():
    id_medico = 2
    id_paciente = 556217

    print("-" * 60)
    print("INICIANDO TESTE DE INTEGRAÇÃO DO SISTEMA")
    print("-" * 60)

    # 1. CRIAR USUÁRIOS
    log("INFO", "Passo 1: Criando Usuários (Serviço GO)")
    try:
        resp_med = requests.post(f"{URL_USERS}/users", json={
            "name": "Dr. House", "email": "house_teste@med.com", "password": "123", "user_type": "doctor"
        })
        doc = resp_med.json()
        
        if 'user_id' in doc:
            id_medico = doc['user_id']
            log("SUCESSO", f"Médico criado. ID: {id_medico}")
        else:
            log("AVISO", f"Retorno inesperado ao criar médico. Usando ID fallback: {id_medico}")

        resp_pac = requests.post(f"{URL_USERS}/users", json={
            "name": "Gusttavo", "email": "gusttavo_teste@client.com", "password": "123", "user_type": "patient"
        })
        pac = resp_pac.json()

        if 'user_id' in pac:
            id_paciente = pac['user_id']
            log("SUCESSO", f"Paciente criado. ID: {id_paciente}")
        else:
            log("AVISO", f"Retorno inesperado ao criar paciente. Usando ID fallback: {id_paciente}")

    except Exception as e:
        log("ERRO", f"Falha na conexão com Serviço de Usuários: {e}")

    # 2. AGENDAR CONSULTA
    log("INFO", "Passo 2: Solicitando Agendamento (Serviço PYTHON)")
    payload_agenda = {
        "medico_id": id_medico,
        "paciente_id": id_paciente,
        "data_hora": "2026-09-20 15:00",
        "especialidade": "Cardiologia",
        "tipo_pagamento": "convenio",
        "detalhes_pagamento": "Unimed"
    }
    
    try:
        resp_agenda = requests.post(f"{URL_AGENDA}/agendar", json=payload_agenda).json()
        id_consulta = resp_agenda.get('id_consulta')
        
        if id_consulta:
            log("SUCESSO", f"Agendamento realizado. ID: {id_consulta}. Status: {resp_agenda.get('status')}")
        else:
            log("FALHA", f"Não foi possível agendar: {resp_agenda}")
            return
            
    except Exception as e:
        log("ERRO FATAL", f"Erro no serviço de agendamento: {e}")
        return

    time.sleep(2)

    # 3. VALIDAR PAGAMENTO
    log("INFO", "Passo 3: Validando Pagamento (Serviço JAVA)")
    payload_validacao = {
        "agendamento_id": id_consulta,
        "paciente_id": id_paciente,
        "tipo_pagamento": "CONVENIO",
        "convenio_nome": "Unimed"
    }
    
    novo_status = "pendente"
    try:
        resp_validacao = requests.post(f"{URL_CONVENIO}/api/convenio/validar", json=payload_validacao).json()
        
        if resp_validacao.get('success'):
            novo_status = "confirmada" if resp_validacao.get('aprovado') else "rejeitada"
            log("SUCESSO", f"Validação concluída. Decisão do sistema: {novo_status.upper()}")
        else:
            log("ERRO", f"Java retornou erro: {resp_validacao.get('error')}")

    except Exception as e:
        log("ERRO", f"Erro ao conectar no Java: {e}")

    # 4. ATUALIZAR STATUS
    log("INFO", "Passo 4: Atualizando Status da Consulta (Python)")
    if novo_status != "pendente":
        try:
            payload_update = {"status": novo_status}
            resp_update = requests.put(f"{URL_AGENDA}/agendar/{id_consulta}", json=payload_update).json()
            log("SUCESSO", f"Status final atualizado no agendamento: {resp_update.get('status')}")
        except Exception as e:
            log("ERRO", f"Erro ao atualizar status: {e}")

    print("-" * 60)
    print("TESTE FINALIZADO")
    print("-" * 60)

if __name__ == "__main__":
    teste_completo()