import os
from dotenv import load_dotenv

load_dotenv()

log_str: str = os.getenv("LOG_FORMAT", f"%(asctime)s | %(name)s | %(lineno)d | %(levelname)s | %(message)s")
log_lvl: str = os.getenv("LOG_LEVEL", "info")
SECRET_KEY: str = os.environ.get("SECRET_KEY", b"bae9543379d8475aa52bd5898fa5a737899a7c5bb4a9b09beec45190e615603d")
ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
OPENAPI_KEY: str = os.getenv("OPENAPI_KEY", "YOUR_API_KEY")
REDIS_HOST: str = os.getenv("REDIS_HOST", 'redis')
REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", None)
REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
TELEGRAM_BOT_TOKEN: str or None = os.getenv("TELEGRAM_BOT_TOKEN", None)
