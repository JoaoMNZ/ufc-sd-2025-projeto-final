FROM golang:alpine

WORKDIR /app

# Copia todo o código fonte
COPY . .

# Inicializa o módulo Go se não existir e baixa dependências
RUN [ ! -f go.mod ] && go mod init users_service || true
RUN go mod tidy

# Compila o servidor
RUN go build -o users_backend main.go

EXPOSE 50051

CMD ["./users_backend"]