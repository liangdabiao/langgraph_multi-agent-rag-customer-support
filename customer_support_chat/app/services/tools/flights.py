from vectorizer.app.vectordb.vectordb import VectorDB
from customer_support_chat.app.core.settings import get_settings
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from customer_support_chat.app.core.humanloop_manager import humanloop_adapter # Import the adapter
import sqlite3
from typing import Optional, Union, List, Dict
from datetime import datetime, date
import pytz

settings = get_settings()
db = settings.SQLITE_DB_PATH
flights_vectordb = VectorDB(table_name="flights", collection_name="flights_collection")


@tool
def fetch_user_flight_information(*, config: RunnableConfig) -> List[Dict]:
    """Fetch all tickets for the user along with corresponding flight information and seat assignments."""
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    query = """
    SELECT 
        t.ticket_no, t.book_ref,
        f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, f.scheduled_departure, f.scheduled_arrival,
        bp.seat_no, tf.fare_conditions
    FROM 
        tickets t
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        JOIN flights f ON tf.flight_id = f.flight_id
        LEFT JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
    WHERE 
        t.passenger_id = ?
    """
    cursor.execute(query, (passenger_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results

@tool
def search_flights(
    query: str,
    limit: int = 2,
) -> List[Dict]:
    """Search for flights based on a natural language query."""
    search_results = flights_vectordb.search(query, limit=limit)

    flights = []
    for result in search_results:
        payload = result.payload
        flights.append({
            "flight_id": payload["flight_id"],
            "flight_no": payload["flight_no"],
            "departure_airport": payload["departure_airport"],
            "arrival_airport": payload["arrival_airport"],
            "scheduled_departure": payload["scheduled_departure"],
            "scheduled_arrival": payload["scheduled_arrival"],
            "status": payload["status"],
            "aircraft_code": payload["aircraft_code"],
            "actual_departure": payload["actual_departure"],
            "actual_arrival": payload["actual_arrival"],
            "chunk": payload["content"],
            "similarity": result.score,
        })
    return flights

@tool
@humanloop_adapter.require_approval(execute_on_reject=False)
async def update_ticket_to_new_flight(
    ticket_no: str, new_flight_id: int, *, config: RunnableConfig, approval_result=None
) -> str:
    """Update the user's ticket to a new valid flight."""
    # If approval is rejected, this function body won't execute.
    # If approval is granted, approval_result will contain the approval details.
    
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Check if the ticket exists and belongs to the passenger
    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
        (ticket_no, passenger_id),
    )
    ticket = cursor.fetchone()
    if not ticket:
        conn.close()
        # This case should ideally not be reached if user intent was confirmed, but we keep the check.
        return f"Ticket {ticket_no} not found for passenger {passenger_id}."

    # Update the flight in ticket_flights
    cursor.execute(
        "UPDATE ticket_flights SET flight_id = ? WHERE ticket_no = ?",
        (new_flight_id, ticket_no),
    )
    conn.commit()

    conn.close()
    if cursor.rowcount > 0:
        return f"Ticket {ticket_no} successfully updated to flight {new_flight_id}."
    else:
        return f"Failed to update ticket {ticket_no}."

@tool
@humanloop_adapter.require_approval(execute_on_reject=False)
async def cancel_ticket(ticket_no: str, *, config: RunnableConfig, approval_result=None) -> str:
    """Cancel the user's ticket and remove it from the database."""
    # If approval is rejected, this function body won't execute.
    # If approval is granted, approval_result will contain the approval details.

    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Check if the ticket exists and belongs to the passenger
    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
        (ticket_no, passenger_id),
    )
    ticket = cursor.fetchone()
    if not ticket:
        conn.close()
        # This case should ideally not be reached if user intent was confirmed, but we keep the check.
        return f"Ticket {ticket_no} not found for passenger {passenger_id}."

    # Delete from ticket_flights
    cursor.execute(
        "DELETE FROM ticket_flights WHERE ticket_no = ?",
        (ticket_no,),
    )
    # Delete from tickets
    cursor.execute(
        "DELETE FROM tickets WHERE ticket_no = ?",
        (ticket_no,),
    )
    conn.commit()

    conn.close()
    return f"Ticket {ticket_no} successfully cancelled."
