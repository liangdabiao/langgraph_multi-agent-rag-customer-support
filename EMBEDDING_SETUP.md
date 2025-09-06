# Embedding API Configuration Guide

## Problem
The api2d.net service doesn't support OpenAI embedding models. This is common with API proxy services that focus on text generation but don't implement embedding endpoints.

## Solution Options

### Option 1: Use Official OpenAI API for Embeddings (Recommended)

1. **Get an official OpenAI API key:**
   - Visit https://platform.openai.com/api-keys
   - Create a new API key

2. **Update your .env file:**
   ```bash
   # Keep api2d.net for text generation
   OPENAI_BASE_URL=https://openai.api2d.net/v1
   OPENAI_API_KEY=fk217050-KDsZ6DATB3qMgwe

   # Add official OpenAI for embeddings
   EMBEDDING_API_KEY=sk-your-official-openai-api-key-here
   EMBEDDING_BASE_URL=https://api.openai.com/v1
   ```

3. **The system will now use:**
   - api2d.net for text generation (GPT models)
   - Official OpenAI for embeddings

### Option 2: Use a Different API Provider

Some alternatives that support embeddings:
- **Together.ai** - Supports various embedding models
- **Replicate** - Has embedding model options  
- **Hugging Face Inference API** - Various embedding models
- **Local embedding models** - Use sentence-transformers

### Option 3: Skip Embedding Generation (Temporary)

If you want to test other parts of the system:

1. Set `RECREATE_COLLECTIONS=False` in .env
2. The system will skip embedding generation and use existing collections

## Cost Considerations

Official OpenAI embedding costs:
- text-embedding-3-small: $0.02 per 1M tokens
- text-embedding-3-large: $0.13 per 1M tokens  
- text-embedding-ada-002: $0.10 per 1M tokens

For typical FAQ data, this costs very little (under $1 for most datasets).

## Next Steps

1. Choose your preferred option above
2. Update your .env file accordingly
3. Run the embedding test: `poetry run python test_embedding.py`
4. If successful, run the vectorizer: `poetry run python vectorizer/app/main.py`

## Files Updated

The following files have been modified to support separate embedding API configuration:
- `.env` - Added EMBEDDING_API_KEY and EMBEDDING_BASE_URL
- `vectorizer/app/core/settings.py` - Added embedding API settings
- `vectorizer/app/vectordb/vectordb.py` - Uses embedding API configuration
- `vectorizer/app/embeddings/embedding_generator.py` - Uses embedding API configuration