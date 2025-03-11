import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "accounting_bot")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "127.0.0.1")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))
WEBAPP_URL = os.getenv("WEBAPP_URL", f"http://{WEBAPP_HOST}:{WEBAPP_PORT}")
