import xmlrpc.client

def validar_enum(valor, permitidos, nome_campo):
    if valor not in permitidos:
        opcoes_str = ", ".join(sorted(list(permitidos)))
        raise xmlrpc.client.Fault(1, f"{nome_campo} inválido. Opções: {opcoes_str}")