import os
from dotenv import load_dotenv
load_dotenv()

def readFile(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()
    

def getEnv(key):
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} not set.")
    return value