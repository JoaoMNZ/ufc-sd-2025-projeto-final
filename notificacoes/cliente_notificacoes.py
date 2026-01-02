import json
import pika
import time

RABBITMQ_HOST = "localhost"
EXCHANGE = "notificacoes"

def callback(ch, method, properties, body):
    try:
        evento = json.loads(body)
        tipo = evento.get("evento", "DESCONHECIDO")
        agendamento = evento.get("agendamento_id", "N/A")

        if tipo == "AGENDAMENTO_CRIADO":
            print(f"[NOTIFICACAO] Agendamento {agendamento} criado. Status: AGUARDANDO VALIDACAO")

        elif tipo == "AGENDAMENTO_CONFIRMADA" or tipo == "AGENDAMENTO_VALIDADO":
            print(f"[NOTIFICACAO] Agendamento {agendamento} CONFIRMADO com sucesso.")

        elif tipo == "AGENDAMENTO_INVALIDO" or tipo == "AGENDAMENTO_REJEITADA":
            print(f"[NOTIFICACAO] Agendamento {agendamento} REJEITADO. Motivo: {evento.get('motivo', 'Reprovado na validacao')}")

        elif tipo == "AGENDAMENTO_CANCELADO":
            print(f"[NOTIFICACAO] Agendamento {agendamento} CANCELADO.")

        else:
            print(f"[INFO] Evento recebido: {evento}")

    except Exception as e:
        print(f"[ERRO] Falha ao processar mensagem: {e}")

def conectar():
    while True:
        try:
            print("[INFO] Conectando ao RabbitMQ...")
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=30
                )
            )
        except pika.exceptions.AMQPConnectionError:
            print("[INFO] Aguardando serviço de mensageria...")
            time.sleep(3)

def main():
    print("--- INICIANDO CLIENTE DE NOTIFICAÇÕES ---")
    connection = conectar()
    print("[INFO] Conexão estabelecida.")
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="fanout"
    )

    queue = channel.queue_declare(queue="", exclusive=True)
    channel.queue_bind(exchange=EXCHANGE, queue=queue.method.queue)

    print("[INFO] Aguardando mensagens...")
    channel.basic_consume(
        queue=queue.method.queue,
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()

if __name__ == "__main__":
    main()