import requests
import sys
import json

# URL base da API REST
BASE_URL = "http://localhost:5000"

def create_user(name, email, password, user_type, cpf="", phone=""):
    """Criar um novo usuário"""
    url = f"{BASE_URL}/users"
    data = {
        "name": name,
        "email": email,
        "password": password,
        "user_type": user_type,
        "cpf": cpf,
        "phone": phone
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def get_user(user_id):
    """Buscar usuário por ID"""
    url = f"{BASE_URL}/users/{user_id}"
    
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def update_user(user_id, name=None, email=None, user_type=None, phone=None):
    """Atualizar dados do usuário"""
    url = f"{BASE_URL}/users/{user_id}"
    data = {}
    
    if name:
        data["name"] = name
    if email:
        data["email"] = email
    if user_type:
        data["user_type"] = user_type
    if phone:
        data["phone"] = phone
    
    response = requests.put(url, json=data)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def delete_user(user_id):
    """Deletar usuário"""
    url = f"{BASE_URL}/users/{user_id}"
    
    response = requests.delete(url)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def list_users(user_type="", limit=50, offset=0):
    """Listar usuários"""
    url = f"{BASE_URL}/users"
    params = {
        "limit": limit,
        "offset": offset
    }
    if user_type:
        params["user_type"] = user_type
    
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total de usuários: {result.get('total', 0)}")
    for user in result.get('users', []):
        print(f"  - ID: {user['user_id']}, Nome: {user['name']}, Email: {user['email']}, Tipo: {user['user_type']}")
    return result

def authenticate_user(email, password):
    """Autenticar usuário (login)"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def print_usage():
    """Imprimir instruções de uso"""
    print("""
Uso: python users_client.py <comando> [argumentos]

Comandos disponíveis:

  create <name> <email> <password> <user_type> [cpf] [phone]
      Criar um novo usuário
      Tipos válidos: patient, doctor, receptionist, admin
      Exemplo: python users_client.py create "João Silva" "joao@email.com" "senha123" "patient" "123.456.789-00" "85999999999"

  get <user_id>
      Buscar usuário por ID
      Exemplo: python users_client.py get 1

  update <user_id> <name> <email> <user_type> [phone]
      Atualizar dados do usuário
      Exemplo: python users_client.py update 1 "João da Silva" "joao.silva@email.com" "patient" "85988888888"

  delete <user_id>
      Deletar usuário
      Exemplo: python users_client.py delete 1

  list [user_type] [limit] [offset]
      Listar usuários (com filtros opcionais)
      Exemplo: python users_client.py list
      Exemplo: python users_client.py list patient 10 0

  login <email> <password>
      Autenticar usuário
      Exemplo: python users_client.py login "joao@email.com" "senha123"
    """)

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "create":
            if len(sys.argv) < 6:
                print("Erro: Argumentos insuficientes para 'create'")
                print("Uso: python users_client.py create <name> <email> <password> <user_type> [cpf] [phone]")
                sys.exit(1)
            
            name = sys.argv[2]
            email = sys.argv[3]
            password = sys.argv[4]
            user_type = sys.argv[5]
            cpf = sys.argv[6] if len(sys.argv) > 6 else ""
            phone = sys.argv[7] if len(sys.argv) > 7 else ""
            
            create_user(name, email, password, user_type, cpf, phone)
        
        elif command == "get":
            if len(sys.argv) < 3:
                print("Erro: Informe o ID do usuário")
                print("Uso: python users_client.py get <user_id>")
                sys.exit(1)
            
            user_id = int(sys.argv[2])
            get_user(user_id)
        
        elif command == "update":
            if len(sys.argv) < 6:
                print("Erro: Argumentos insuficientes para 'update'")
                print("Uso: python users_client.py update <user_id> <name> <email> <user_type> [phone]")
                sys.exit(1)
            
            user_id = int(sys.argv[2])
            name = sys.argv[3]
            email = sys.argv[4]
            user_type = sys.argv[5]
            phone = sys.argv[6] if len(sys.argv) > 6 else None
            
            update_user(user_id, name, email, user_type, phone)
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("Erro: Informe o ID do usuário")
                print("Uso: python users_client.py delete <user_id>")
                sys.exit(1)
            
            user_id = int(sys.argv[2])
            delete_user(user_id)
        
        elif command == "list":
            user_type = sys.argv[2] if len(sys.argv) > 2 else ""
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
            offset = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            
            list_users(user_type, limit, offset)
        
        elif command == "login":
            if len(sys.argv) < 4:
                print("Erro: Informe email e senha")
                print("Uso: python users_client.py login <email> <password>")
                sys.exit(1)
            
            email = sys.argv[2]
            password = sys.argv[3]
            authenticate_user(email, password)
        
        else:
            print(f"Comando '{command}' não reconhecido")
            print_usage()
            sys.exit(1)
    
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar ao servidor. Verifique se está rodando.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()