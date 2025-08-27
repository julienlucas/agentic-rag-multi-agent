import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from .constants import MAX_FILE_SIZE, MAX_TOTAL_SIZE, ALLOWED_TYPES

load_dotenv()

class Settings(BaseSettings):
    # Paramètres requis
    MISTRALAI_API_KEY: str = os.getenv("MISTRALAI_API_KEY")
    MODEL_ID: str = "mistral-large-latest"
    MODEL_OCR_ID: str = "mistral-ocr-latest"
    EMBEDDING_MODEL_ID: str = "mistral-embed"

    # Paramètres optionnels avec valeurs par défaut
    MAX_FILE_SIZE: int = MAX_FILE_SIZE
    MAX_TOTAL_SIZE: int = MAX_TOTAL_SIZE
    ALLOWED_TYPES: list = ALLOWED_TYPES

    # Paramètres de base de données
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "documents"

    # Paramètres de récupération
    VECTOR_SEARCH_K: int = 10
    HYBRID_RETRIEVER_WEIGHTS: list = [0.4, 0.6]

    # Paramètres de journalisation
    LOG_LEVEL: str = "INFO"

    # Nouveaux paramètres de cache avec annotations de type
    CACHE_DIR: str = "document_cache"
    CACHE_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()