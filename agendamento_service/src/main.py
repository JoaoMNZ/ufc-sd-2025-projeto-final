import sys
import os
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

sys.path.append(os.getcwd())

from src.config import Config
from src.service.agendamento_service import AgendamentoService

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def main():
    address = ('0.0.0.0', Config.RPC_PORT)

    server = ThreadedXMLRPCServer(address, allow_none=True)

    service = AgendamentoService()
    server.register_instance(service)
    server.register_introspection_functions()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
