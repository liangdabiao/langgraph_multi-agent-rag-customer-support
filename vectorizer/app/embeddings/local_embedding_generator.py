"""
Local embedding generator using sentence-transformers
No API calls required - works offline
"""

import sys
import os
from typing import Union, List
import numpy as np

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

try:
    from vectorizer.app.core.settings import get_settings
    from vectorizer.app.core.logger import logger
    settings = get_settings()
except ImportError:
    # Fallback for direct execution
    print("Running in standalone mode - using default settings")
    
    class MockSettings:
        LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    settings = MockSettings()
    
    # Simple logger fallback
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
    
    logger = SimpleLogger()

# Global model instance
_model = None

def get_local_model():
    """Get or initialize the local embedding model"""
    global _model
    
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model_name = settings.LOCAL_EMBEDDING_MODEL
            logger.info(f"Loading local embedding model: {model_name}")
            
            # Try to load the model
            _model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded local model: {model_name}")
            logger.info(f"Model embedding dimension: {_model.get_sentence_embedding_dimension()}")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load local model {model_name}: {str(e)}")
            logger.info("Trying fallback model: all-MiniLM-L6-v2")
            try:
                _model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Successfully loaded fallback model: all-MiniLM-L6-v2")
            except Exception as fallback_error:
                logger.error(f"Failed to load fallback model: {str(fallback_error)}")
                raise
    
    return _model

def generate_local_embedding(content: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Generate embeddings using local sentence-transformers model
    
    Args:
        content: String or list of strings to embed
        
    Returns:
        Embedding vector(s) as list(s) of floats
    """
    try:
        model = get_local_model()
        
        if isinstance(content, str):
            # Single string
            embedding = model.encode(content)
            return embedding.tolist()
            
        elif isinstance(content, list):
            # List of strings
            embeddings = model.encode(content)
            return [emb.tolist() for emb in embeddings]
            
        else:
            raise ValueError("Content must be either a string or a list of strings")
            
    except Exception as e:
        logger.error(f"Error generating local embeddings: {str(e)}")
        raise

def test_local_embeddings():
    """Test the local embedding generation"""
    try:
        logger.info("Testing local embedding generation...")
        
        test_texts = [
            "Hello world",
            "This is a test sentence",
            "Local embeddings are working!"
        ]
        
        # Test single string
        single_embedding = generate_local_embedding(test_texts[0])
        logger.info(f"Single embedding shape: {len(single_embedding)}")
        logger.info(f"First 5 values: {single_embedding[:5]}")
        
        # Test multiple strings
        batch_embeddings = generate_local_embedding(test_texts)
        logger.info(f"Batch embeddings shape: {len(batch_embeddings)} x {len(batch_embeddings[0])}")
        
        logger.info("Local embedding test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Local embedding test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test when run directly
    test_local_embeddings()