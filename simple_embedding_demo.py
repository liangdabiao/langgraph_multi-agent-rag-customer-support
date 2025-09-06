import os
from langchain_openai import OpenAIEmbeddings

# --- Configuration ---
# Ensure the OPENAI_API_KEY environment variable is set.
# You can set it in your terminal like this:
# Linux/macOS: export OPENAI_API_KEY='your-api-key-here'
# Windows (Command Prompt): set OPENAI_API_KEY=your-api-key-here
# Windows (PowerShell): $env:OPENAI_API_KEY="your-api-key-here"

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

print(API_KEY)
print(BASE_URL)
MODEL_NAME = "text-embedding-ada-002"
# ----------------------

def generate_embeddings(texts, model=MODEL_NAME):
    """
    Generates embeddings for a list of texts using the specified model.

    Args:
        texts (list of str): The texts to embed.
        model (str): The name of the embedding model to use.

    Returns:
        list: A list of embedding vectors.
    """
    # Configure OpenAI embeddings
    if BASE_URL:
        embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=API_KEY,
            openai_api_base=BASE_URL
        )
    else:
        embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=API_KEY
        )
    
    try:
        # Generate embeddings
        if isinstance(texts, str):
            return [embeddings.embed_query(texts)]
        elif isinstance(texts, list):
            return embeddings.embed_documents(texts)
        else:
            raise ValueError("Content must be either a string or a list of strings")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise # Re-raise the exception for debugging

if __name__ == "__main__":
    print(f"Generating embeddings using model: {MODEL_NAME}")
    
    # Example texts
    texts_to_embed = [
        "The quick brown fox jumps over the lazy dog.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Embeddings are a powerful tool in natural language processing."
    ]
    
    try:
        embeddings = generate_embeddings(texts_to_embed)
        
        print(f"\nSuccessfully generated {len(embeddings)} embeddings.")
        print(f"Dimension of the first embedding: {len(embeddings[0])}")
        print(f"First 5 elements of the first embedding: {embeddings[0][:5]}")
        
        # Basic check: all embeddings should have the same length
        lengths = [len(e) for e in embeddings]
        if all(l == lengths[0] for l in lengths):
            print(f"All embeddings have consistent dimension: {lengths[0]}")
        else:
             print(f"Warning: Embedding dimensions are inconsistent: {lengths}")

    except Exception as e:
        print(f"Demo failed: {e}")