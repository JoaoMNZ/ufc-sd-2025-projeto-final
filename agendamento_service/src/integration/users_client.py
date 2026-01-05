import grpc
import os
from src.pb import users_pb2, users_pb2_grpc

class UsersClient:
    def __init__(self):
        self.address = os.getenv("GRPC_ADDRESS")
        self.channel = grpc.insecure_channel(self.address)
        self.stub = users_pb2_grpc.UserServiceStub(self.channel)

    def get_user_role(self, requester_id, target_id):
        try:
            response = self.stub.GetUser(
                users_pb2.GetUserRequest(
                    token=int(requester_id),
                    user_id=int(target_id)
                )
            )
            return users_pb2.UserType.Name(response.user_type)

        except grpc.RpcError as e:
            raise Exception(e.details())

        except Exception as e:
            raise Exception(f"Erro interno no servidor")