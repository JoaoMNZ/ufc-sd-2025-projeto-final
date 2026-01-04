import psycopg2
from src.database.connection import get_connection

class AgendamentoError(Exception):
    pass

class AgendamentoRepository:
    def create(self, paciente_id, medico_id, data, horario, especialidade, tipo_pagamento):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                INSERT INTO agendamento (paciente_id, medico_id, data, horario, especialidade, tipo_pagamento)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            cursor.execute(query, (paciente_id, medico_id, data, horario, especialidade, tipo_pagamento))
            novo_id = cursor.fetchone()[0]
            conn.commit()
            return novo_id

        except psycopg2.IntegrityError as e:
            conn.rollback()
            erro_str = str(e)
            
            if "uk_horario_medico" in erro_str:
                raise AgendamentoError("Médico indisponível neste horário.")
            if "uk_horario_paciente" in erro_str:
                raise AgendamentoError("Paciente já possui um agendamento neste horário.")
            
            raise AgendamentoError("Dados inválidos (verifique se paciente/médico existem).")
            
        except Exception as e:
            conn.rollback()
            raise e 
        
        finally:
            cursor.close()
            conn.close()