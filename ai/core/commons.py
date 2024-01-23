import os
import pathlib

from dotenv import load_dotenv

path: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.absolute()
load_dotenv(f'{path}/.env')

SECRET_KEY: str = os.getenv("SECRET_KEY", b"bae9543379d8475aa52bd5898fa5a737899a7c5bb4a9b09beec45190e615603d")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
OPENAPI_KEY: str = os.getenv("OPENAPI_KEY", "YOUR_API_KEY")
REDIS_HOST: str = os.getenv("REDIS_HOST", 'redis')
REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD: str or None = os.getenv("REDIS_PASSWORD", None)
REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
TELEGRAM_BOT_TOKEN: str or None = os.getenv("TELEGRAM_BOT_TOKEN", None)
APP_HOST: str = os.getenv('APP_HOST', "0.0.0.0")
APP_PORT: int = int(os.getenv('APP_PORT', 8000))
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'info')
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s | %(name)s | %(lineno)d | %(levelname)s | %(message)s")
VERSION: str = os.getenv("VERSION", "0.0.1")
GRADIO_PORT: str = os.getenv("GRADIO_PORT", "7860")
GRADIO_INPUTS: str = os.getenv("GRADIO_INPUTS", "text")
GRADIO_OUTPUTS: str = os.getenv("GRADIO_OUTPUTS", "text")
GRADIO_TITLE: str = os.getenv("GRADIO_TITLE", "OpenAI")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
DEBUG: bool = os.getenv("DEBUG", False)
GRADIO: bool = os.getenv("GRADIO", False)
TELEGRAM: bool = os.getenv("TELEGRAM", False)
SHARE: bool = os.getenv("SHARE", False)
AUTH: str or None = os.getenv("AUTH", None)
DOMAIN: str = os.getenv("DOMAIN", "localhost")
IN_BROWSER: bool = os.getenv("IN_BROWSER", False)
METHOD: str = os.getenv("METHOD", "http")
TOPIC: str = os.getenv("TOPIC", "Python")
ROLE: str = os.getenv("ROLE", "Eres una IA muy eficaz y experta en {{topic}} respondes dudas enseñas con tutoriales y/o ejemplos.")
