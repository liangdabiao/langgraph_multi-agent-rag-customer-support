# Qwen Code Context for `multi-agent-rag-customer-support-main`

## Project Overview

This project implements a **Multi-Agent Retrieval-Augmented Generation (RAG) System** for customer support, specifically tailored for a travel context (e.g., Swiss Airlines). It's built using Python with key libraries like **LangChain** and **LangGraph**.

The core idea is to have a primary assistant that handles general queries and routes more complex, specialized tasks (like booking flights, cars, hotels, or excursions) to dedicated sub-assistants. This architecture enhances modularity, scalability, and allows for fine-grained control, especially over sensitive operations which require user confirmation.

**Key Features:**
*   **Multi-Agent Architecture:** Utilizes LangGraph to define a stateful workflow with a primary assistant and specialized assistants.
*   **RAG Integration:** Employs a Qdrant vector database for efficient retrieval of relevant information (e.g., flight details, policies) to augment the LLM's responses.
*   **Safety Mechanisms:** Implements "sensitive tools" that pause the workflow and require explicit user approval before execution.
*   **Observability:** Integrates with LangSmith for tracing and monitoring the agent interactions.
*   **Modular Design:** Code is structured into distinct modules (`customer_support_chat`, `vectorizer`) for clear separation of concerns.

## Project Structure

```
E:\multi-agent-rag-customer-support-main\
├── .dev.env                # Template for environment variables
├── .gitignore
├── docker-compose.yml      # Defines services like Qdrant
├── Dockerfile
├── Makefile                # Defines common project commands
├── poetry.lock             # Poetry dependency lock file
├── pyproject.toml          # Project metadata and dependencies (Poetry)
├── README.md               # Main project documentation
├── .vscode\                # VS Code configuration
│   └── launch.json
├── customer_support_chat\  # Main application module
│   ├── README.md           # Detailed module documentation
│   ├── __init__.py
│   ├── app\                # Core application logic
│   │   ├── __init__.py
│   │   ├── core\           # Core components (state, settings, logger)
│   │   ├── data\           # (Potentially) local data files
│   │   ├── graph.py        # Defines the LangGraph workflow
│   │   ├── main.py         # Main entry point for the chat application
│   │   └── services\       # Assistants, tools, utilities, vector DB interface
│   └── data\               # Local SQLite database (travel2.sqlite)
├── graphs\                 # Output directory for graph visualizations
│   └── multi-agent-rag-system-graph.png
├── images\                 # Images for documentation
└── vectorizer\             # Module for generating embeddings and populating Qdrant
    ├── README.md           # Detailed module documentation
    ├── __init__.py
    └── app\                # Core vectorization logic
        ├── __init__.py
        ├── core\           # Core components (logger, settings)
        ├── embeddings\     # Embedding generation logic
        ├── main.py         # Entry point for the vectorization process
        └── vectordb\       # Qdrant database interaction logic
```

## Main Technologies

*   **Language:** Python 3.12+
*   **Package Manager:** Poetry
*   **Core Frameworks/Libraries:**
    *   `langgraph`: For building the multi-agent state machine/graph.
    *   `langchain`: For LLM interaction, prompts, and tools.
    *   `langchain-openai`: For OpenAI LLM and embedding integration.
    *   `qdrant-client`: For interacting with the Qdrant vector database.
*   **Vector Database:** Qdrant (can be run locally via Docker)
*   **Data Source:** SQLite database (`travel2.sqlite`) containing travel-related data.
*   **Observability:** LangSmith (optional)
*   **Environment Management:** `python-dotenv`

## Building and Running

**Prerequisites:**
*   Python 3.12+
*   Poetry
*   Docker and Docker Compose
*   OpenAI API Key
*   LangSmith API Key (optional)

**Setup & Execution Steps:**

1.  **Environment Setup:**
    *   Copy the environment template: `cp .dev.env .env`
    *   Edit `.env` and fill in your `OPENAI_API_KEY` and optionally `LANGCHAIN_API_KEY`.

2.  **Install Dependencies:**
    *   Run `poetry install` to install all Python dependencies defined in `pyproject.toml`.

3.  **Prepare Vector Database (Qdrant):**
    *   Start the Qdrant service in the background: `docker compose up qdrant -d`
    *   *(Optional)* Access the Qdrant UI at `http://localhost:6333/dashboard#`.

4.  **Generate and Store Embeddings:**
    *   Run the vectorizer to process data and populate Qdrant: `poetry run python vectorizer/app/main.py`

5.  **Run the Customer Support Chat Application:**
    *   Start the main chat application: `poetry run python ./customer_support_chat/app/main.py`
    *   Interact with the chatbot via the command line. Type `quit`, `exit`, or `q` to stop.

## Development Conventions

*   **Dependency Management:** Dependencies are managed using Poetry (`pyproject.toml`, `poetry.lock`).
*   **Modularity:** Code is split into the `vectorizer` and `customer_support_chat` modules. Each module has its own `README.md`.
*   **State Management:** Uses `langgraph.checkpoint.memory.MemorySaver` for in-memory state persistence across conversation turns.
*   **Graph Definition:** The conversation flow is defined in `customer_support_chat/app/graph.py` using LangGraph's `StateGraph`.
*   **Assistants:** Specialized assistants inherit from a base class in `customer_support_chat/app/services/assistants/assistant_base.py`.
*   **Tools:** Tools (functions the LLM can call) are defined in `customer_support_chat/app/services/tools/`.
*   **Configuration:** Application settings are managed via Pydantic models in `core/settings.py`, loading from environment variables.
*   **Logging:** Uses a custom logger configured in `core/logger.py`.

## Qwen Added Memories
- 在生成包含多行文本的 Markdown 文件时，直接在 write_file 的 content 参数中使用 '
' 字符串会导致文件内容中出现字面量的 
，而不是实际的换行符。正确的做法是在 Python 字符串中使用实际的换行符（例如，使用三重引号 ''' 或 """ 包裹多行字符串，或在字符串中使用 
 但确保它被解释为换行符而不是字面量）。当需要从包含字面量 
 的文件创建正确格式的文件时，必须使用脚本（如 PowerShell 或 Python）来替换这些字面量。
- 用户希望为当前的多智能体RAG客服系统增加多用户支持功能，包括：1) 允许多个用户同时使用；2) 保存用户的聊天记录；3) 提供一个HTML形式的用户聊天界面。
