import requests
import sys
import os
from datetime import datetime

BASE_URL = "http://localhost:5000"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def ler_numero(mensagem):
    """Lê um número inteiro do usuário com validação de erro."""
    while True:
        try:
            valor = input(mensagem)
            return int(valor)
        except ValueError:
            print("[ERRO] Entrada invalida. Por favor, digite um numero inteiro.")

def ler_data():
    """Lê data e hora com validação e tentativa de reentrada."""
    print("\n--- DATA E HORA DA CONSULTA ---")
    while True:
        try:
            dia = ler_numero("Dia (1-31): ")
            mes = ler_numero("Mes (1-12): ")
            ano = ler_numero("Ano (AAAA): ")
            hora = ler_numero("Hora (06-18): ")

            # Tenta criar o objeto data para validar calendário (ex: evita 30 de fevereiro)
            data_obj = datetime(ano, mes, dia, hora, 0)
            
            # Formata para o padrão esperado pelo sistema
            return data_obj.strftime("%Y-%m-%d %H:00")
        except ValueError:
            print("[ERRO] Data ou hora invalida (ex: dia inexistente ou hora fora do intervalo). Tente novamente.")

def ler_pagamento():
    """Lê os dados de pagamento com menu de opções."""
    print("\n--- FORMA DE PAGAMENTO ---")
    print("1 - Convenio")
    print("0 - Particular")
    
    while True:
        opcao = input("Selecione a opcao: ")
        
        if opcao == '1':
            while True:
                nome = input("Nome do Convenio: ").strip()
                if nome:
                    return "convenio", nome
                print("[ERRO] O nome do convenio nao pode ser vazio.")
                
        elif opcao == '0':
            while True:
                cartao = input("Numero do Cartao: ").strip()
                if cartao:
                    # Remove espaços para enviar limpo
                    return "particular", cartao.replace(" ", "")
                print("[ERRO] O numero do cartao nao pode ser vazio.")
        
        else:
            print("[ERRO] Opcao invalida. Digite 1 ou 0.")

def menu_principal():
    print("\n========================================")
    print("      SISTEMA DE AGENDAMENTO CLIENTE      ")
    print("========================================")
    print("1. Agendar Nova Consulta")
    print("2. Listar Minhas Consultas")
    print("3. Confirmar/Alterar Status de Consulta")
    print("0. Sair")
    return input("Digite sua opcao: ")

def rotina_agendar():
    print("\n[NOVO AGENDAMENTO]")
    
    # Coleta de dados com validação
    medico_id = ler_numero("ID do Medico: ")
    paciente_id = ler_numero("ID do Paciente: ")
    data_hora = ler_data()
    
    while True:
        especialidade = input("Especialidade: ").strip()
        if especialidade:
            break
        print("[ERRO] Especialidade obrigatoria.")

    tipo_pag, detalhes = ler_pagamento()

    payload = {
        "medico_id": medico_id,
        "paciente_id": paciente_id,
        "data_hora": data_hora,
        "especialidade": especialidade,
        "tipo_pagamento": tipo_pag,
        "detalhes_pagamento": detalhes
    }

    print("\n[INFO] Enviando requisicao ao servidor...")
    try:
        resp = requests.post(f"{BASE_URL}/agendar", json=payload, timeout=5)
        
        print("-" * 40)
        print(f"STATUS HTTP: {resp.status_code}")
        
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get("status") == "sucesso":
                print(f"[SUCESSO] Agendamento REALIZADO. ID: {dados.get('id_consulta')}")
                print(f"Mensagem: {dados.get('mensagem')}")
            else:
                print(f"[FALHA] O servidor recusou o agendamento.")
                print(f"Motivo: {dados.get('mensagem')}")
        else:
            print(f"[ERRO] Resposta inesperada: {resp.text}")
            
    except requests.exceptions.ConnectionError:
        print("[ERRO CRITICO] Nao foi possivel conectar ao servidor (localhost:5000). Verifique se o Docker esta rodando.")
    except Exception as e:
        print(f"[ERRO] Ocorreu uma excecao: {e}")

def rotina_listar():
    print("\n[LISTAR CONSULTAS]")
    try:
        resp = requests.get(f"{BASE_URL}/consultas", timeout=5)
        if resp.status_code == 200:
            consultas = resp.json()
            if not consultas:
                print("[INFO] Nenhuma consulta encontrada no sistema.")
            else:
                print(f"{'ID':<5} | {'DATA/HORA':<20} | {'STATUS'}")
                print("-" * 40)
                for c in consultas:
                    print(f"{c.get('id',0):<5} | {c.get('data_hora',''):<20} | {c.get('status','').upper()}")
                print("-" * 40)
        else:
            print(f"[ERRO] Falha ao listar: {resp.text}")
    except Exception as e:
        print(f"[ERRO] Falha de conexao: {e}")

def rotina_confirmar():
    print("\n[ATUALIZAR STATUS]")
    id_consulta = ler_numero("Digite o ID da consulta: ")
    
    print("Novo status desejado:")
    print("1 - confirmada")
    print("2 - cancelada")
    
    status_map = {'1': 'confirmada', '2': 'cancelada'}
    
    while True:
        op = input("Opcao: ")
        if op in status_map:
            novo_status = status_map[op]
            break
        print("[ERRO] Opcao invalida.")

    payload = {"status": novo_status}
    
    try:
        resp = requests.put(f"{BASE_URL}/agendar/{id_consulta}", json=payload, timeout=5)
        if resp.status_code == 200:
            print(f"[SUCESSO] {resp.json().get('mensagem')}")
        else:
            print(f"[ERRO] {resp.text}")
    except Exception as e:
        print(f"[ERRO] Falha de conexao: {e}")

# Loop Principal
if __name__ == "__main__":
    try:
        while True:
            opcao = menu_principal()
            
            if opcao == '1':
                rotina_agendar()
            elif opcao == '2':
                rotina_listar()
            elif opcao == '3':
                rotina_confirmar()
            elif opcao == '0':
                print("[INFO] Encerrando cliente.")
                sys.exit(0)
            else:
                print("[ERRO] Opcao invalida, tente novamente.")
                
            input("\nPressione ENTER para continuar...")
            limpar_tela()
            
    except KeyboardInterrupt:
        print("\n[INFO] Interrupcao forçada. Saindo...")