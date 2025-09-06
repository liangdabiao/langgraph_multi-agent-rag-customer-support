import os
import shutil
import sqlite3
from datetime import datetime
import pandas as pd
import requests
from customer_support_chat.app.core.settings import get_settings
from customer_support_chat.app.core.logger import logger
from qdrant_client import QdrantClient
from customer_support_chat.app.core.settings import get_settings
from typing import List, Dict, Callable

from langchain_core.messages import ToolMessage
from customer_support_chat.app.core.state import State

settings = get_settings()


def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        # Handle ALL tool calls in the message, not just the first one
        last_message = state["messages"][-1]
        tool_messages = []
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_messages.append(
                    ToolMessage(
                        content=(
                            f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user. "
                            f"The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name}, "
                            "and the booking, update, or other action is not complete until after you have successfully invoked the appropriate tool. "
                            "If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control. "
                            "Do not mention who you are—just act as the proxy for the assistant."
                        ),
                        tool_call_id=tool_call["id"],
                    )
                )
        else:
            # Fallback for cases where no tool calls are found (shouldn't happen in normal delegation)
            tool_messages.append(
                ToolMessage(
                    content=(
                        f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user. "
                        f"The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name}, "
                        "and the booking, update, or other action is not complete until after you have successfully invoked the appropriate tool. "
                        "If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control. "
                        "Do not mention who you are—just act as the proxy for the assistant."
                    ),
                    tool_call_id="fallback_tool_call_id",
                )
            )
        
        return {
            "messages": tool_messages,
            "dialog_state": new_dialog_state,
        }
    return entry_node


def download_and_prepare_db():
    settings = get_settings()
    db_file = settings.SQLITE_DB_PATH
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db_url = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
    if not os.path.exists(db_file):
        response = requests.get(db_url)
        response.raise_for_status()
        with open(db_file, "wb") as f:
            f.write(response.content)
        update_dates(db_file)

def update_dates(db_file):
    backup_file = db_file + '.backup'
    if not os.path.exists(backup_file):
        shutil.copy(db_file, backup_file)

    conn = sqlite3.connect(db_file)

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    tdf["bookings"]["book_date"] = (
        pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True)
        + time_diff
    )

    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    for column in datetime_columns:
        tdf["flights"][column] = (
            pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            {
                "type": "tool",
                "content": f"Error: {repr(error)}\nPlease fix your mistakes.",
                "tool_call_id": tc["id"],
            }
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list):
    from langchain_core.messages import ToolMessage
    from langchain_core.runnables import RunnableLambda
    from langgraph.prebuilt import ToolNode

    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def get_qdrant_client():
    settings = get_settings()
    try:
        # Use API key if provided (for cloud Qdrant), otherwise connect without it (for local)
        if settings.QDRANT_KEY:
            client = QdrantClient(
                url=settings.QDRANT_URL, 
                api_key=settings.QDRANT_KEY,
                timeout=60  # Increase timeout to 60 seconds
            )
        else:
            client = QdrantClient(url=settings.QDRANT_URL, timeout=60)
        # Test the connection
        collections = client.get_collections()
        logger.info(f"Connected to Qdrant successfully. Found {len(collections.collections)} existing collections.")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant server at {settings.QDRANT_URL}. Error: {str(e)}")
        raise

def flight_info_to_string(flight_info: List[Dict]) -> str:
    info_lines = [] 
    i = 0
    for flight in flight_info:
        i += 1
        line = (
            f"Ticket [{i}]:\n"
            f"Ticket Number: {flight['ticket_no']}\n"
            f"Booking Reference: {flight['book_ref']}\n"
            f"Flight ID: {flight['flight_id']}\n"
            f"Flight Number: {flight['flight_no']}\n"
            f"Departure: {flight['departure_airport']} at {flight['scheduled_departure']}\n"
            f"Arrival: {flight['arrival_airport']} at {flight['scheduled_arrival']}\n"
            f"Seat: {flight['seat_no']}\n"
            f"Fare Class: {flight['fare_conditions']}\n"
            f"\n\n"
        )
        info_lines.append(line)

    info_lines = f"User current booked flight(s) details:\n" + "\n".join(info_lines)

    return "\n".join(info_lines)