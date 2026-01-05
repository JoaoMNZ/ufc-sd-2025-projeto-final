import os

class Config:
    VALIDATION_HOST = "0.0.0.0"
    VALIDATION_PORT = int(os.getenv("VALIDATION_PORT"))
    BUFFER_SIZE = 4096