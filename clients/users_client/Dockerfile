FROM python:3.10-slim

WORKDIR /app

COPY users_client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY users_client/ .

COPY utils/ ./utils

RUN mkdir -p pb && touch pb/__init__.py
RUN touch utils/__init__.py

RUN python -m grpc_tools.protoc -Iproto --python_out=pb --grpc_python_out=pb proto/users.proto
RUN sed -i 's/^import users_pb2/from . import users_pb2/' pb/users_pb2_grpc.py

CMD ["tail", "-f", "/dev/null"]