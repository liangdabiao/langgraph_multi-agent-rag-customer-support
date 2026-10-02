from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY: str = environ.get("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = environ.get("OPENAI_BASE_URL", "")
    
    # Model configuration for cost optimization
    OPENAI_MODEL: str = environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS: int = int(environ.get("MAX_TOKENS", "1000"))  # Limit tokens to control costs
    
    DATA_PATH: str = "./customer_support_chat/data"
    LOG_LEVEL: str = environ.get("LOG_LEVEL", "DEBUG")
    SQLITE_DB_PATH: str = environ.get(
        "SQLITE_DB_PATH", "./customer_support_chat/data/travel2.sqlite"
    )
    QDRANT_URL: str = environ.get("QDRANT_URL", "http://localhost:6333")
    QDRANT_KEY: str = environ.get("QDRANT_KEY", "")
    RECREATE_COLLECTIONS: bool = environ.get("RECREATE_COLLECTIONS", "False")
    LIMIT_ROWS: int = environ.get("LIMIT_ROWS", "100")
    
    # WooCommerce API Settings
    # WOOCOMMERCE_API_URL should be the WordPress base URL (e.g., "https://yourstore.com")
    # The system will automatically append "/wp-json/wc/v3" to create the full API endpoint
    WOOCOMMERCE_CONSUMER_KEY: str = environ.get("WOOCOMMERCE_CONSUMER_KEY", "")
    WOOCOMMERCE_CONSUMER_SECRET: str = environ.get("WOOCOMMERCE_CONSUMER_SECRET", "")
    WOOCOMMERCE_API_URL: str = environ.get("WOOCOMMERCE_API_URL", "")
    
    # Form Submission API Settings
    FORM_SUBMISSION_API_URL: str = environ.get("FORM_SUBMISSION_API_URL", "")
    
    # Blog Search API Settings
    BLOG_SEARCH_API_URL: str = environ.get("BLOG_SEARCH_API_URL", "")
    
    # You.com Search Settings (optional web-search backend, opt-in)
    # When enabled, the primary assistant uses You.com web search
    # (keyless MCP free profile by default) instead of DuckDuckGo.
    YOUCOM_SEARCH_ENABLED: bool = environ.get("YOUCOM_SEARCH_ENABLED", "False").lower() in ("1", "true", "yes", "on")
    YOUCOM_MCP_URL: str = environ.get("YOUCOM_MCP_URL", "https://api.you.com/mcp?profile=free")
    YOUCOM_API_KEY: str = environ.get("YOUCOM_API_KEY", environ.get("YDC_API_KEY", ""))

def get_settings():
    return Config()