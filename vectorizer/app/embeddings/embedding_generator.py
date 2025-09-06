from langchain_openai import OpenAIEmbeddings
from vectorizer.app.core.settings import get_settings
from vectorizer.app.core.logger import logger
from typing import Union, List

settings = get_settings()

# Configure OpenAI embeddings with embedding-specific configuration
if settings.EMBEDDING_BASE_URL:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.EMBEDDING_API_KEY,
        openai_api_base=settings.EMBEDDING_BASE_URL
    )
else:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.EMBEDDING_API_KEY
    )

def generate_embedding(content: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Generate embeddings using either API or local model based on configuration
    """
    # Check if local embeddings are enabled
    if settings.USE_LOCAL_EMBEDDINGS:
        logger.info("Using local embeddings")
        try:
            from .local_embedding_generator import generate_local_embedding
            return generate_local_embedding(content)
        except Exception as e:
            logger.error(f"Local embedding failed: {str(e)}")
            logger.info("Falling back to API embeddings...")
    
    # Use API embeddings
    logger.info("Using API embeddings")
    try:
        if isinstance(content, str):
            return embeddings.embed_query(content)
        elif isinstance(content, list):
            return embeddings.embed_documents(content)
        else:
            raise ValueError("Content must be either a string or a list of strings")
    except Exception as e:
        logger.error(f"API embedding failed: {str(e)}")
        
        # If API fails and local embeddings aren't enabled, try to enable them
        if not settings.USE_LOCAL_EMBEDDINGS:
            logger.info("API failed, attempting to use local embeddings as fallback...")
            try:
                from .local_embedding_generator import generate_local_embedding
                return generate_local_embedding(content)
            except Exception as local_e:
                logger.error(f"Local embedding fallback also failed: {str(local_e)}")
                raise Exception(f"Both API and local embeddings failed. API error: {str(e)}, Local error: {str(local_e)}")
        else:
            raise
