# Simple Embedding Generation Demo

This script demonstrates how to generate embeddings using the `text-embedding-3-large` model from OpenAI.

## Prerequisites

1.  Python 3.6+
2.  `openai` Python library (`pip install openai`)
3.  An OpenAI API key set as the environment variable `OPENAI_API_KEY`.

## Code

```python
# simple_embedding_demo.py

import os
from openai import OpenAI

# --- Configuration ---
# Ensure the OPENAI_API_KEY environment variable is set.
# You can set it in your terminal like this:
# Linux/macOS: export OPENAI_API_KEY='your-api-key-here'
# Windows (Command Prompt): set OPENAI_API_KEY=your-api-key-here
# Windows (PowerShell): $env:OPENAI_API_KEY="your-api-key-here"

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

MODEL_NAME = "text-embedding-3-large"
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
    client = OpenAI(api_key=API_KEY)
    
    try:
        response = client.embeddings.create(
            model=model,
            input=texts
        )
        # Extract embeddings from the response
        embeddings = [item.embedding for item in response.data]
        return embeddings
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

```

## How to Run

1.  Save the code above as `simple_embedding_demo.py`.
2.  Open your terminal or command prompt.
3.  Set your OpenAI API key:
    ```bash
    export OPENAI_API_KEY='your-actual-openai-api-key-here'
    # Or on Windows PowerShell:
    # $env:OPENAI_API_KEY="your-actual-openai-api-key-here"
    ```
4.  Navigate to the directory where you saved the file.
5.  Run the script:
    ```bash
    python simple_embedding_demo.py
    ```

## Expected Output (Format)

The output will vary based on the actual embeddings generated, but it should look similar to this:

```
Generating embeddings using model: text-embedding-3-large

Successfully generated 3 embeddings.
Dimension of the first embedding: 3072
First 5 elements of the first embedding: [0.00123, -0.00456, 0.00789, ...]
All embeddings have consistent dimension: 3072
```