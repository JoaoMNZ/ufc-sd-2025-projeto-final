FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY proto/ ./proto

RUN mkdir -p src/pb && touch src/pb/__init__.py

RUN python -m grpc_tools.protoc -Iproto --python_out=src/pb --grpc_python_out=src/pb proto/users.proto
RUN sed -i 's/^import users_pb2/from . import users_pb2/' src/pb/users_pb2_grpc.py

CMD ["python", "src/main.py"]