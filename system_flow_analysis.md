# System Flow Analysis

This document provides a technical analysis of the system's startup process and execution flow.

## 1. System Startup (`main.py`)

When the system is initiated via `poetry run python ./customer_support_chat/app/main.py`, the following sequence occurs:

*   **Database Preparation:** The `download_and_prepare_db()` function ensures the SQLite database (`travel2.sqlite`) is present in the `customer_support_chat/data/` directory. If missing, it downloads it from a predefined URL. It also updates date fields in the database to reflect current times.
*   **Graph Visualization:** The system generates a visual representation of the LangGraph workflow and saves it as `graphs/multi-agent-rag-system-graph.png`.
*   **Session Initialization:**
    *   A unique session `thread_id` and a fixed `passenger_id` are set in the configuration.
    *   `thread_id`: Used by `langgraph.checkpoint.MemorySaver` to persist conversation state in memory. This enables multi-turn conversations within a session.
    *   `passenger_id`: Hardcoded as `"5102 899977"`. This ID is crucial for retrieving user-specific information, particularly flight bookings, from the SQLite database. Currently, the system operates as if all users were this single passenger.
*   **Main Interaction Loop:**
    *   The system enters an infinite `while True:` loop.
    *   It prompts the user for input using `input("User: ")`.
    *   If the user types 'quit', 'exit', or 'q', the loop breaks, and the program exits.
    *   Otherwise, the user's input is processed by the `multi_agentic_graph`.

## 2. Graph Execution (`graph.py`, `state.py`)

The `multi_agentic_graph` (an instance of `langgraph.graph.StateGraph`) defines the workflow. The state of this graph is managed by the `State` TypedDict (`customer_support_chat/app/core/state.py`), which includes `messages` (conversation history), `user_info` (retrieved flight details), and `dialog_state` (current assistant context).

*   **Initial State:** Execution always starts at the `fetch_user_info` node.
*   **`fetch_user_info` Node:** This node calls `fetch_user_flight_information` (from `tools.flights`) using the `passenger_id` from the config to retrieve the user's current flight bookings. This information is stored in the `State` under the `user_info` key.
*   **Primary Assistant:** After fetching user info, control is passed to the `primary_assistant` node. This assistant analyzes the user's input and the current `State` (including `user_info`).
*   **Routing Logic:** The `primary_assistant` uses its LLM and tools to determine the next step:
    *   If it can handle the request directly (e.g., answering a general question using RAG), it interacts with its tools (like `primary_assistant_tools` node) and responds.
    *   If the request requires a specialized task (flight update, car rental, hotel booking, excursion), it invokes a corresponding "To..." tool (e.g., `ToFlightBookingAssistant`). This signals the graph to delegate the task.
*   **Specialized Assistants:** If delegation occurs, the graph routes to an `enter_...` node (e.g., `enter_update_flight`), which sets up the context for the specialized assistant (e.g., `update_flight`). This assistant then takes over, interacting with its specific tools.
*   **Tool Execution:**
    *   Assistants call tools by generating `tool_calls`.
    *   The graph routes these calls to corresponding `..._tools` nodes (e.g., `update_flight_safe_tools`, `update_flight_sensitive_tools`).
    *   **Safe Tools:** Tools deemed safe (e.g., `search_flights`, `search_hotels`) are executed directly. Their results are fed back to the calling assistant.
    *   **Sensitive Tools:** Tools that modify data or perform critical actions (e.g., `update_ticket_to_new_flight`, `cancel_ticket`) are flagged as sensitive.
*   **Human-in-the-Loop (HITL) for Sensitive Actions:**
    *   When a sensitive tool is about to be executed, the graph is configured with `interrupt_before=["..._sensitive_tools"]`.
    *   This causes `graph.stream()` to pause *before* the sensitive tool node runs.
    *   Control returns to `main.py`.

## 3. Human Interaction (`main.py`)

The `main.py` script handles the pause caused by the interrupt:

*   **Interrupt Detection:** After `graph.stream()`, `main.py` calls `multi_agentic_graph.get_state(config)`. If the returned `snapshot.next` is not empty, it signifies an interrupt (a pending sensitive action).
*   **User Prompt:** `main.py` presents a prompt to the user, displaying the pending action and asking for approval: `input("\nDo you approve of the above actions? Type 'y' to continue; otherwise, explain your requested changes.\n\n")`.
*   **Approval Handling:**
    *   If the user types 'y', `main.py` calls `multi_agentic_graph.invoke(None, config)`. This tells the graph to resume execution and proceed with the sensitive tool.
    *   If the user provides any other input, `main.py` assumes it's feedback/denial. It constructs a `ToolMessage` containing the user's input and the `tool_call_id` of the pending action. It then calls `multi_agentic_graph.invoke()` with this message. The graph routes this message back to the assistant that requested the sensitive action, allowing it to adjust its behavior based on the user's feedback.
*   **Continuation:** After handling the interrupt, `main.py` continues its loop, processing any new messages generated by the resumed graph execution and then waiting for the next user input.

This cycle of user input -> graph processing -> potential HITL pause -> user response -> graph continuation forms the core interaction loop of the system.

## 4. Data Sources

The system relies on two primary data sources:

*   **Qdrant Vector Database:** Used for Retrieval-Augmented Generation (RAG). Assistants use search tools (e.g., `search_flights`) to query this database for relevant information to augment their responses. The data in Qdrant originates from the SQLite database and other sources, processed and embedded by the `vectorizer` module.
*   **SQLite (`travel2.sqlite`):** Stores structured data like user tickets, flight details, bookings. Tools like `fetch_user_flight_information`, `update_ticket_to_new_flight`, and `cancel_ticket` directly query or modify this database. The `passenger_id` from the configuration is essential for these database interactions to ensure data isolation for the (currently hardcoded) user.