from flask import Flask, request, jsonify
import grpc
import os
import sys

# Importar os arquivos gerados do proto
import users_pb2
import users_pb2_grpc

app = Flask(__name__)

# Configuração do cliente gRPC
GRPC_HOST = os.getenv('GRPC_HOST', 'localhost')
GRPC_PORT = os.getenv('GRPC_PORT', '50051')

def get_grpc_stub():
    channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
    return users_pb2_grpc.UserServiceStub(channel)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['name', 'email', 'password', 'user_type']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        stub = get_grpc_stub()
        grpc_request = users_pb2.CreateUserRequest(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            user_type=data['user_type'],
            cpf=data.get('cpf', ''),
            phone=data.get('phone', '')
        )
        
        response = stub.CreateUser(grpc_request)
        
        if not response.success:
            return jsonify({'error': response.message}), 400
        
        return jsonify({
            'user_id': response.user_id,
            'name': response.name,
            'email': response.email,
            'user_type': response.user_type,
            'cpf': response.cpf,
            'phone': response.phone,
            'created_at': response.created_at,
            'message': response.message
        }), 201
        
    except grpc.RpcError as e:
        return jsonify({'error': f'gRPC error: {e.details()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        stub = get_grpc_stub()
        grpc_request = users_pb2.GetUserRequest(user_id=user_id)
        response = stub.GetUser(grpc_request)
        
        if not response.success:
            return jsonify({'error': response.message}), 404
        
        return jsonify({
            'user_id': response.user_id,
            'name': response.name,
            'email': response.email,
            'user_type': response.user_type,
            'cpf': response.cpf,
            'phone': response.phone,
            'created_at': response.created_at
        }), 200
        
    except grpc.RpcError as e:
        return jsonify({'error': f'gRPC error: {e.details()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        
        stub = get_grpc_stub()
        grpc_request = users_pb2.UpdateUserRequest(
            user_id=user_id,
            name=data.get('name', ''),
            email=data.get('email', ''),
            user_type=data.get('user_type', ''),
            phone=data.get('phone', '')
        )
        
        response = stub.UpdateUser(grpc_request)
        
        if not response.success:
            return jsonify({'error': response.message}), 400
        
        return jsonify({
            'user_id': response.user_id,
            'name': response.name,
            'email': response.email,
            'user_type': response.user_type,
            'phone': response.phone,
            'message': response.message
        }), 200
        
    except grpc.RpcError as e:
        return jsonify({'error': f'gRPC error: {e.details()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        stub = get_grpc_stub()
        grpc_request = users_pb2.DeleteUserRequest(user_id=user_id)
        response = stub.DeleteUser(grpc_request)
        
        if not response.success:
            return jsonify({'error': response.message}), 404
        
        return jsonify({'message': response.message}), 200
        
    except grpc.RpcError as e:
        return jsonify({'error': f'gRPC error: {e.details()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def list_users():
    try:
        user_type = request.args.get('user_type', '')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        stub = get_grpc_stub()
        grpc_request = users_pb2.ListUsersRequest(
            user_type=user_type,
            limit=limit,
            offset=offset
        )
        
        response = stub.ListUsers(grpc_request)
        
        users = []
        for user in response.users:
            users.append({
                'user_id': user.user_id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type,
                'cpf': user.cpf,
                'phone': user.phone,
                'created_at': user.created_at
            })
        
        return jsonify({
            'users': users,
            'total': response.total
        }), 200
        
    except grpc.RpcError as e:
        return jsonify({'error': f'gRPC error: {e.details()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
        
        stub = get_grpc_stub()
        grpc_request = users_pb2.AuthRequest(
            email=data['email'],
            password=data['password']
        )
        
        response = stub.AuthenticateUser(grpc_request)
        
        if not response.success:
            return jsonify({'error': response.message}), 401
        
        return jsonify({
            'user_id': response.user_id,
            'user_type': response.user_type,
            'token': response.token,
            'message': response.message
        }), 200
        
    except grpc.RpcError as e:
        return jsonify({'error': f'gRPC error: {e.details()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)