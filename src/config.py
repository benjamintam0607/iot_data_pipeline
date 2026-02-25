import os
from dotenv import load_dotenv


load_dotenv()

def get_config():
    return {
        "target_directory": os.getenv("TARGET_DIR", "data/input"),
        "database_path": os.getenv("DB_PATH", "data/iot.db")
    }