from os import environ
from dotenv import load_dotenv


load_dotenv()

class Config:
    OPENAI_API_KEY: str = environ.get("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = environ.get("OPENAI_BASE_URL", "")
    
    # Separate embedding API configuration
    EMBEDDING_API_KEY: str = environ.get("EMBEDDING_API_KEY", environ.get("OPENAI_API_KEY"))
    EMBEDDING_BASE_URL: str = environ.get("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
    
    # Local embedding configuration
    USE_LOCAL_EMBEDDINGS: bool = environ.get("USE_LOCAL_EMBEDDINGS", "false").lower() == "true"
    LOCAL_EMBEDDING_MODEL: str = environ.get("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    SQLITE_DB_PATH: str = environ.get("SQLITE_DB_PATH", "./customer_support_chat/data/travel2.sqlite")
    QDRANT_URL: str = environ.get("QDRANT_URL", "http://localhost:6333")
    QDRANT_KEY: str = environ.get("QDRANT_KEY", "")
    RECREATE_COLLECTIONS: bool = environ.get("RECREATE_COLLECTIONS", "False")

def get_settings():
    return Config()
