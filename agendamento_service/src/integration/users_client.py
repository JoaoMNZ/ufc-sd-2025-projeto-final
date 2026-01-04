import grpc
import os
from src.pb import users_pb2, users_pb2_grpc

class UsersClient:
    def __init__(self):
        self.address = os.getenv("GRPC_ADDRESS")

    def get_user_role(self, requester_id, target_id):
        try:
            with grpc.insecure_channel(self.address) as channel:
                stub = users_pb2_grpc.UserServiceStub(channel)
                
                response = stub.GetUser(
                    users_pb2.GetUserRequest(
                        token=int(requester_id), 
                        user_id=int(target_id)
                    )
                )
                
                return users_pb2.UserType.Name(response.user_type)

        except grpc.RpcError as e:
            raise Exception(f"{e.details()}")

        except Exception as e:
            raise Exception(f"Erro interno no servidor")