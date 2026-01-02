from flask import Flask, request, jsonify
import grpc
import sys
import os

# Adiciona o diretório atual ao path para importar os stubs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import users_pb2
import users_pb2_grpc

app = Flask(__name__)

# --- CORREÇÃO AQUI ---
# Pega o endereço do ambiente (Docker) ou usa localhost como fallback
GRPC_SERVER = os.getenv('GRPC_SERVER', 'localhost:50051')
print(f"🔗 Conectando ao gRPC em: {GRPC_SERVER}") 

def get_grpc_stub():
    channel = grpc.insecure_channel(GRPC_SERVER)
    return users_pb2_grpc.UserServiceStub(channel)

# --- Mapeamento de Strings para ENUMs ---
def string_to_role(role_str):
    roles = {
        "admin": users_pb2.ADMINISTRADOR,
        "doctor": users_pb2.MEDICO,
        "receptionist": users_pb2.RECEPCIONISTA,
        "patient": users_pb2.PACIENTE
    }
    return roles.get(role_str.lower(), users_pb2.PACIENTE) # Default: Paciente

def role_to_string(role_enum):
    return str(role_enum)

# --- Rotas REST ---

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    stub = get_grpc_stub()
    
    try:
        response = stub.CreateUser(users_pb2.CreateUserRequest(
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            user_type=string_to_role(data.get('user_type', 'patient'))
        ))
        return jsonify({
            "user_id": response.user_id,
            "name": response.name,
            "email": response.email,
            "user_type": response.user_type,
            "message": "Usuário criado com sucesso"
        }), 201
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    stub = get_grpc_stub()
    try:
        response = stub.GetUser(users_pb2.GetUserRequest(user_id=user_id))
        return jsonify({
            "user_id": response.user_id,
            "name": response.name,
            "email": response.email,
            "user_type": response.user_type
        })
    except grpc.RpcError as e:
        return jsonify({"error": "Usuário não encontrado ou erro interno"}), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    stub = get_grpc_stub()
    try:
        response = stub.DeleteUser(users_pb2.DeleteUserRequest(user_id=user_id))
        return jsonify({
            "success": response.success,
            "message": response.message
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    stub = get_grpc_stub()
    try:
        response = stub.AuthenticateUser(users_pb2.AuthRequest(
            email=data.get('email'),
            password=data.get('password')
        ))
        
        if response.success:
            return jsonify({
                "success": True,
                "token": response.token,
                "user_id": response.user_id,
                "message": response.message
            })
        else:
            return jsonify({"success": False, "message": "Credenciais inválidas"}), 401
            
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 500

# Rota extra para listar (opcional)
@app.route('/users', methods=['GET'])
def list_users():
    stub = get_grpc_stub()
    u_type = request.args.get('user_type', '')
    limit = int(request.args.get('limit', 50))
    
    enum_type = string_to_role(u_type) if u_type else 0 

    try:
        response = stub.ListUsers(users_pb2.ListUsersRequest(
            user_type=enum_type,
            limit=limit
        ))
        
        users_list = []
        for u in response.users:
            users_list.append({
                "user_id": u.user_id,
                "name": u.name,
                "email": u.email,
                "user_type": u.user_type
            })
            
        return jsonify({"users": users_list, "total": response.total})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 500

if __name__ == '__main__':
    print("Interface REST rodando na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)