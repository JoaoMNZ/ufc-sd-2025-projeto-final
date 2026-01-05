import os

class Config:
    HOST = "0.0.0.0"
    PORT = int(os.getenv("VALIDATION_PORT"))
    BUFFER_SIZE = 4096