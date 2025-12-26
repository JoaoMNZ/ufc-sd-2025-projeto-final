import requests
import json
import time

BASE_URL = "http://localhost:5000"

def imprimir_resposta(passo, response):
    print(f"\n--- {passo} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print("Resposta:", json.dumps(response.json(), indent=4))
    except:
        print("Resposta (texto):", response.text)

# TESTE 1: Agendamento Ideal (Hora Cheia + Pagamento)
url_agendar = f"{BASE_URL}/agendar"
payload_ok = {
    "medico_id": 10,
    "paciente_id": 556217, # Seu ID
    "data_hora": "2026-03-15 08:00", # hora cheia ok
    "especialidade": "Ortopedia",
    "tipo_pagamento": "convenio",
    "detalhes_pagamento": "Unimed"
}
resp = requests.post(url_agendar, json=payload_ok)
imprimir_resposta("Teste 1: Agendamento Correto (Deve passar)", resp)


# TESTE 2: Hora Quebrada (Deve Falhar)
# o grupo decidiu que so aceita hora cheia
payload_hora_ruim = payload_ok.copy()
payload_hora_ruim["data_hora"] = "2026-03-15 08:30" 
resp = requests.post(url_agendar, json=payload_hora_ruim)
imprimir_resposta("Teste 2: Hora Quebrada 8:30 (Deve falhar)", resp)


# TESTE 3: Conflito de Paciente 
# o paciente ja tem consulta as 08:00 (do teste 1)
# vamos tentar marcar ele as 08:00 com OUTRO medico
payload_conflito = {
    "medico_id": 20, # Outro medico
    "paciente_id": 556217, # MESMO Paciente
    "data_hora": "2026-03-15 08:00", # Mesma hora
    "especialidade": "Dermatologia",
    "tipo_pagamento": "particular",
    "detalhes_pagamento": "4444555566667777"
}
resp = requests.post(url_agendar, json=payload_conflito)
imprimir_resposta("Teste 3: Paciente duplicado (Deve falhar)", resp)


# TESTE 4: Atualizar Status
# simulando o validador aprovando o pagamento
url_atualizar = f"{BASE_URL}/agendar/1"
payload_status = { "status": "validado" }

resp = requests.put(url_atualizar, json=payload_status)
imprimir_resposta("Teste 4: Atualiza Status para 'validado'", resp)