import os
from datetime import timedelta
from dotenv import load_dotenv

# Lokasi folder aplikasi
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Buat folder instance di dalam folder proyek PKM
INSTANCE_PATH = os.path.join(PROJECT_ROOT, 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

# Path absolut file database SQLite
DB_PATH = os.path.join(INSTANCE_PATH, 'pkm_sdit.db').replace('\\', '/')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Gunakan path absolut yang dijamin ada
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False