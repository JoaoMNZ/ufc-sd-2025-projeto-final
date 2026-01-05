import socket
import json

from src.config import Config
from src.validation.payment_validator import PaymentValidator

class ValidationServer:

    def __init__(self):
        self.validator = PaymentValidator()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((Config.VALIDATION_HOST, Config.VALIDATION_PORT))
            server.listen()

            while True:
                conn, _ = server.accept()
                with conn:
                    self.handle_request(conn)

    def handle_request(self, conn):
        data = conn.recv(Config.BUFFER_SIZE)
        if not data:
            return

        try:
            payload = json.loads(data.decode())

            tipo_pagamento = payload["tipo_pagamento"]
            dados_pagamento = payload["dados_pagamento"]

            status = self.validator.validate(
                tipo_pagamento,
                dados_pagamento
            )

            response = {"status": status}

        except Exception:
            response = {"erro": "erro interno no servidor"}

        conn.sendall(json.dumps(response).encode())