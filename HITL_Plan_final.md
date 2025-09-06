# Multi-Agent RAG Customer Support System - Human-in-the-Loop (HITL) Plan

## Current System Analysis

Based on the code review, here's how the system currently works:

1.  **Entry Point (`main.py`)**:
    *   The system starts by ensuring the SQLite database (`travel2.sqlite`) is present.
    *   It generates and saves a visualization of the LangGraph workflow.
    *   A unique session `thread_id` and a fixed `passenger_id` are set in the configuration.
    *   It enters an infinite loop, reading user input from the command line (`input("User: ")`).
    *   User input is processed by the `multi_agentic_graph` (defined in `graph.py`) using `graph.stream()`.

2.  **Graph Execution (`graph.py`)**:
    *   The graph uses `langgraph.checkpoint.MemorySaver` with `interrupt_before` on sensitive tool nodes (e.g., `update_flight_sensitive_tools`).
    *   When an interrupt occurs (before a sensitive tool is executed), the graph execution pauses.
    *   The `main.py` loop detects this paused state by checking if `snapshot.next` (from `graph.get_state()`) is not empty.

3.  **Human-in-the-Loop Interaction (`main.py`)**:
    *   Upon detecting an interrupt, `main.py` manually presents a prompt to the user: `input("\nDo you approve of the above actions? Type 'y' to continue; otherwise, explain your requested changes.\n\n")`.
    *   Based on the user's response:
        *   If the user types 'y', `main.py` calls `graph.invoke(None, config)` to continue the graph execution.
        *   If the user provides any other input (feedback/denial), `main.py` creates a `ToolMessage` containing the user's feedback and calls `graph.invoke()` with this message. This message is then accessible to the assistant that triggered the interrupt.

4.  **State and Memory**:
    *   The `MemorySaver` checkpointer stores the conversation state (messages, `user_info`, `dialog_state`) in memory, keyed by the `thread_id`.
    *   This allows the conversation to persist across multiple turns within the same session (as long as the process runs).

## Proposed HITL Enhancements

To improve the current HITL mechanism, we can make the following changes:

1.  **Refactor HITL Logic into the Graph**:
    *   The current HITL loop in `main.py` tightly couples the CLI interface with the HITL logic. This makes it hard to reuse the graph in other contexts (e.g., a web API).
    *   We can move the HITL logic into the graph itself using a dedicated "human-in-the-loop" node. This node would be responsible for pausing execution and waiting for external input.
    *   The graph would then have a clear path for handling approvals and denials, making the flow more explicit and manageable.

2.  **Standardize Interrupt Handling**:
    *   Currently, the graph only interrupts *before* sensitive tool nodes. We can standardize this by creating a generic "request approval" mechanism.
    *   Specialized assistants (like `flight_booking_assistant`) would call a new `RequestApproval` tool when they need human confirmation.
    *   The graph's conditional routing would detect calls to `RequestApproval` and route to the new HITL node.

3.  **Implement the HITL Node**:
    *   The HITL node would be a stateless function that signals to the outside world that human input is required.
    *   Instead of blocking (like `input()`), it would update the `State` to indicate that an approval is pending, perhaps storing the details of the request and the `tool_call_id`.
    *   The graph execution would then pause at this node.

4.  **Modify the Interface Layer (`main.py`)**:
    *   `main.py` (or any other interface, like a web API handler) would need to be updated to handle this new state.
    *   After each `graph.stream()` call, it would check the final state.
    *   If the state indicates that human approval is pending (e.g., by checking a new field in `State` like `approval_pending: bool` or by seeing if the current `dialog_state` is "waiting_for_approval"), it would present the request to the human user.
    *   The user's response (approval or feedback) would then be fed back into the graph using `graph.invoke()`, similar to the current approach but using a standardized `ProvideApproval` tool or a specific message format.

5.  **Benefits of Refactoring**:
    *   **Decoupling**: The core logic of the agents and the HITL mechanism is separated from the specific interface (CLI, Web, etc.).
    *   **Clarity**: The graph definition explicitly shows where human intervention can occur.
    *   **Reusability**: The same graph can be used in different environments with different ways of handling the human interaction.
    *   **Maintainability**: Changes to the HITL process only need to be made in the graph and the interface layer, not scattered across `main.py`'s loop.

This refactored approach would make the system more robust and adaptable for future integrations while keeping the human-in-the-loop functionality intact and potentially more sophisticated.

