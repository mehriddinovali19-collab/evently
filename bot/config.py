import os 
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
BOT_API_SECRET = env('BOT_API_SECRET', default='my-very-secure-secret-token-123')
BACKEND_API_URL = env('BACKEND_API_URL', default='http://localhost:8000/api/v1')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN topilmadi! iltimos, env aylni to'ldiring")

