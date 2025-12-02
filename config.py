# config.py
import os
from dotenv import load_dotenv

# load the .env file from the same folder
_here = os.path.dirname(__file__)
load_dotenv(os.path.join(_here, ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Copy .env.example -> .env and add your key.")

