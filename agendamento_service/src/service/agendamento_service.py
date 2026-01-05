import xmlrpc.client
from src.repository.agendamento_repository import AgendamentoRepository, AgendamentoError
from src.integration.users_client import UsersClient
from src.utils.validators import validar_enum

class AgendamentoService:
    def __init__(self):
        self.agendamento_repository = AgendamentoRepository()
        self.users_client = UsersClient()

        self.ESPECIALIDADES = {'CARDIOLOGIA', 'PEDIATRIA', 'ORTOPEDIA', 'DERMATOLOGIA'}
        self.PAGAMENTOS = {'CONVENIO', 'PARTICULAR'}

    def agendar_consulta(self, token, paciente_id, medico_id, data, horario, especialidade, tipo_pagamento, dados_pagamento):
        if not all([token, paciente_id, medico_id, data, horario, especialidade, tipo_pagamento, dados_pagamento]):
             raise xmlrpc.client.Fault(1, "Todos os campos são obrigatórios.")

        try:
            if not (6 <= horario <= 16):
                raise xmlrpc.client.Fault(1, "Horário inválido. A clínica funciona das 06:00 às 17:00.")
            
            validar_enum(especialidade, self.ESPECIALIDADES, "Especialidade")
            validar_enum(tipo_pagamento, self.PAGAMENTOS, "Tipo de Pagamento")

            # Consulta role do requisitante (token == requisitante_id).
            requester_role = self.users_client.get_user_role(token, token)

            if requester_role == "PACIENTE":
                if int(token) != int(paciente_id):
                    raise xmlrpc.client.Fault(1, "Paciente só pode agendar consultas para si mesmo.")
            
            elif requester_role == "RECEPCIONISTA":
                pass
            
            else:
                raise xmlrpc.client.Fault(1, "Apenas Pacientes e Recepcionistas podem criar agendamentos.")

            paciente_role = self.users_client.get_user_role(token, paciente_id)
            if paciente_role != "PACIENTE":
                raise xmlrpc.client.Fault(1, f"O ID informado ({paciente_id}) não pertence a um Paciente.")

            medico_role = self.users_client.get_user_role(token, medico_id)
            if medico_role != "MEDICO":
                raise xmlrpc.client.Fault(1, f"O ID informado ({medico_id}) não pertence a um Médico.")


            agendamento_id = self.agendamento_repository.create(
                paciente_id, medico_id, data, horario, especialidade, tipo_pagamento
            )

            # --- 5. ORQUESTRAÇÃO FUTURA ---
            # self.validador.validar(agendamento_id, dados_pagamento)
            
            return {
                "id": agendamento_id,
                "status": "PENDENTE",
                "mensagem": "Agendamento realizado. Aguardando validação financeira."
            }

        except AgendamentoError as e:
            raise xmlrpc.client.Fault(1, str(e))
            
        except Exception as e:
            msg = str(e)
            if "interno" in msg.lower():
                 raise xmlrpc.client.Fault(2, msg)
            else:
                 raise xmlrpc.client.Fault(1, msg)