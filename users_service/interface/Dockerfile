FROM python:3.9-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da interface
COPY . .

# Expõe a porta do Flask
EXPOSE 5000

# Comando para iniciar
CMD ["python", "rest_api.py"]