import json
import os

SESSION_FILE = os.path.expanduser("~/.med_session/session.json")

def save_session(token):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    
    data = {
        "token": token
    }
    
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        raise Exception("Você não está logado. Faça o login primeiro.")
    
    with open(SESSION_FILE, "r") as f:
        return json.load(f)["token"]
