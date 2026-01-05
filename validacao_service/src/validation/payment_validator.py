class PaymentValidator:

    def validate(self, tipo_pagamento, dados_pagamento):
        tipo_pagamento = str(tipo_pagamento).upper()

        if tipo_pagamento == "CONVENIO":
            return self._validate_convenio(dados_pagamento)

        if tipo_pagamento == "PARTICULAR":
            return self._validate_particular(dados_pagamento)

        return "REJEITADO"

    def _validate_convenio(self, nome_convenio):
        try:
            return "CONFIRMADO" if len(str(nome_convenio)) % 2 == 0 else "REJEITADO"
        except Exception:
            return "REJEITADO"

    def _validate_particular(self, numero_cartao):
        try:
            ultimo_digito = int(str(numero_cartao)[-1])
            return "CONFIRMADO" if ultimo_digito % 2 == 0 else "REJEITADO"
        except Exception:
            return "REJEITADO"
