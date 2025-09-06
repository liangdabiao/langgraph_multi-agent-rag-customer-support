
# Vectorizer Module

This module is responsible for handling embeddings and vector database operations. The following sections outline the main components of the module, which was designed with flexibility in mind, utilizing design patterns to allow easy adaptation to various vector databases. The architecture enables straightforward integration of different database solutions, ensuring scalability and maintainability. By abstracting the embedding generation and document indexing logic, this module can be seamlessly extended or modified to suit specific use cases or database backends without changing the core functionality.

Additionally, the module was designed to function as a Python package, allowing it to be hosted in a private repository and integrated into automated processes. This means it can be leveraged by tools like Airflow or other pipeline automation systems, enabling efficient embedding and vector database operations as part of a larger workflow.

## Structure
```
vectorizer
├── README.md
├── __init__.py
└── app
    ├── core
    │   ├── __init__.py
    │   ├── logger.py
    │   └── settings.py
    ├── embeddings
    │   ├── __init__.py
    │   └── embedding_generator.py
    ├── main.py
    └── vectordb
        ├── __init__.py
        ├── chunkenizer.py
        ├── utils.py
        └── vectordb.py
```

### 1. `embedding_generator.py`

This file generates embeddings for the input content using the OpenAI API. It handles both single strings and lists of strings as inputs.

- **Function: `generate_embedding`**
  - **Input:** `Union[str, List[str]]` - Accepts either a single string or a list of strings.
  - **Output:** Returns a list of floats (embedding) or a list of lists of floats if a list of strings is provided.

### 2. `chunkenizer.py`

This file handles the splitting of large texts into smaller chunks using the `RecursiveCharacterTextSplitter` from LangChain.

- **Function: `recursive_character_splitting`**
  - **Input:** Text, chunk size, and chunk overlap.
  - **Output:** Returns chunks of text to be used for further processing or embedding generation.

### 3. `vectordb.py`

This is the core component of the vectorizer module that handles interactions with Qdrant for storing and retrieving vector embeddings. It also manages SQLite database connections and content formatting.

- **Class: `VectorDB`**
  - **Methods:**
    - `__init__`: Initializes the vector DB with table name, collection name, and optionally creates the collection.
    - `connect_to_qdrant`: Connects to the Qdrant client using the provided settings.
    - `create_or_clear_collection`: Creates a new collection or clears the existing one.
    - `format_content`: Formats content for different collection types (car rentals, flights, hotels, etc.).
    - `generate_embedding_async`: Generates embeddings asynchronously using the OpenAI API.
    - `create_embeddings_async`: Main function for handling embedding creation for various content types.
    - `index_regular_docs`: Indexes regular documents from SQLite into Qdrant.
    - `index_faq_docs`: Handles the FAQ documents and indexes them into Qdrant.
    - `create_embeddings`: Runs the async process for generating embeddings.
    - `search`: Performs a vector search on the Qdrant collection.

- **Asynchronous Processing:**
  - Uses `asyncio` and `aiohttp` to handle batch processing of documents and interact with the OpenAI API efficiently.
  - **Batching:** Chunks are processed in batches to avoid exceeding rate limits.

### 4. `main.py`

This file is responsible for creating and indexing multiple collections (car rentals, trips, flights, hotels, and FAQ) into Qdrant.

- **Function: `create_collections`**
  - Initializes vector DB for each table and collection, generates embeddings, and stores them in Qdrant.

### 5. `utils.py`

Contains utility functions that support various operations in the module.

## How to Use

1. **Creating Embeddings**:
   - Run `main.py` to initialize vector databases for the various collections and generate embeddings for them.
   - Example command: `python main.py`

2. **Searching**:
   - Use the `search` function from `vectordb.py` to perform searches against the indexed embeddings in Qdrant.

## Notes

- Ensure the OpenAI API key is set in the environment variables or through the settings file before running the embedding generation.
- The `RecursiveCharacterTextSplitter` is used for splitting large pieces of text into manageable chunks to ensure effective embedding generation.
