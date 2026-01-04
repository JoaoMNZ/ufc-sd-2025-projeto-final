import grpc
import argparse
import os

import pb.users_pb2 as users_pb2
import pb.users_pb2_grpc as users_pb2_grpc

from utils.session_manager import save_session
from utils.session_manager import load_session

GRPC_ADDRESS = os.getenv("GRPC_ADDRESS")

def handle_rpc_error(e: grpc.RpcError):
    print(f"Erro gRPC [{e.code().name}]: {e.details()}")

def auth(stub, args):
    try:
        response = stub.AuthenticateUser(
            users_pb2.AuthRequest(
                email=args.email,
                password=args.password
            )
        )

        save_session(response.token)

        print(f"Bem-vindo, {response.name}!")
        
    except grpc.RpcError as e:
        handle_rpc_error(e)

def create_user(stub, args):
    try:
        session = load_session()

        response = stub.CreateUser(
            users_pb2.CreateUserRequest(
                token=session,
                name=args.name,
                email=args.email,
                password=args.password,
                user_type=users_pb2.UserType.Value(args.user_type)
            )
        )

        print("Usuário criado com sucesso")
        tipo = users_pb2.UserType.Name(response.user_type)
        print(f"ID: {response.user_id} | Nome: {response.name} | Email: {response.email} | Tipo: {tipo}")

    except grpc.RpcError as e:
        handle_rpc_error(e)
    except ValueError:
        print("Erro: Tipo de usuário inválido.")
    except Exception as e:
        print(f"Erro: {e}")

def get_user(stub, args):
    try:
        session = load_session()

        response = stub.GetUser(
            users_pb2.GetUserRequest(
                token=session, 
                user_id=args.user_id
            )
        )

        tipo = users_pb2.UserType.Name(response.user_type)
        print(f"ID: {response.user_id} | Nome: {response.name} | Email: {response.email} | Tipo: {tipo}")

    except grpc.RpcError as e:
        handle_rpc_error(e)
    except Exception as e:
        print(f"Erro: {e}")


def list_users(stub, args):
    try:
        session = load_session()

        target_type = users_pb2.UNKNOWN_ROLE
        if args.user_type:
            target_type = users_pb2.UserType.Value(args.user_type)

        response = stub.ListUsers(
            users_pb2.ListUsersRequest(
                token=session,
                user_type=target_type
            )
        )

        for user in response.users:
            tipo = users_pb2.UserType.Name(user.user_type)
            print(f"ID: {user.user_id} | Nome: {user.name} | Email: {user.email} | Tipo: {tipo}")

    except grpc.RpcError as e:
        handle_rpc_error(e)
    except ValueError:
        print("Erro: Tipo de usuário inválido.")
    except Exception as e:
        print(f"Erro: {e}")


def update_user(stub, args):
    try:
        session = load_session()

        response = stub.UpdateUser(
            users_pb2.UpdateUserRequest(
                token=session,
                user_id=args.user_id,
                name=args.name or "",
                email=args.email or "",
                password=args.password or ""
            )
        )
        
        print("Usuário atualizado com sucesso!")
        tipo = users_pb2.UserType.Name(response.user_type)
        print(f"ID: {response.user_id} | Nome: {response.name} | Email: {response.email} | Tipo: {tipo}")

    except grpc.RpcError as e:
        handle_rpc_error(e)
    except Exception as e:
        print(f"Erro: {e}")


def delete_user(stub, args):
    try:
        session = load_session()

        stub.DeleteUser(
            users_pb2.DeleteUserRequest(
                token=session,
                user_id=args.user_id
            )
        )
        print("Usuário deletado com sucesso.")

    except grpc.RpcError as e:
        handle_rpc_error(e)
    except Exception as e:
        print(f"Erro: {e}")


def main():
    parser = argparse.ArgumentParser(description="Cliente gRPC - User Service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("auth")
    auth_parser.add_argument("--email", required=True)
    auth_parser.add_argument("--password", required=True)

    create_parser = subparsers.add_parser("create-user")
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--email", required=True)
    create_parser.add_argument("--password", required=True)
    create_parser.add_argument(
        "--user-type",
        required=True,
        choices=["ADMINISTRADOR", "MEDICO", "RECEPCIONISTA", "PACIENTE"]
    )

    get_parser = subparsers.add_parser("get-user")
    get_parser.add_argument("--user-id", type=int, required=True)

    list_parser = subparsers.add_parser("list-users")
    list_parser.add_argument(
        "--user-type",
        required=False,
        choices=["ADMINISTRADOR", "MEDICO", "RECEPCIONISTA", "PACIENTE"]
    )

    update_parser = subparsers.add_parser("update-user")
    update_parser.add_argument("--user-id", type=int, required=True)
    update_parser.add_argument("--name", required=False)
    update_parser.add_argument("--email", required=False)
    update_parser.add_argument("--password", required=False)

    delete_parser = subparsers.add_parser("delete-user")
    delete_parser.add_argument("--user-id", type=int, required=True)

    args = parser.parse_args()

    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = users_pb2_grpc.UserServiceStub(channel)

        match args.command:
            case "auth":
                auth(stub, args)
            case "create-user":
                create_user(stub, args)
            case "get-user":
                get_user(stub, args)
            case "list-users":
                list_users(stub, args)
            case "update-user":
                update_user(stub, args)
            case "delete-user":
                delete_user(stub, args)


if __name__ == "__main__":
    main()
