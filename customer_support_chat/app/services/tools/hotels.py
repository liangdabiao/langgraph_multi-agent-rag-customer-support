from vectorizer.app.vectordb.vectordb import VectorDB
from customer_support_chat.app.core.settings import get_settings
from langchain_core.tools import tool
from customer_support_chat.app.core.humanloop_manager import humanloop_adapter # Import the adapter
import sqlite3
from typing import Optional, Union, List, Dict
from datetime import datetime, date

settings = get_settings()
db = settings.SQLITE_DB_PATH
hotels_vectordb = VectorDB(table_name="hotels", collection_name="hotels_collection")

@tool
def search_hotels(
    query: str,
    limit: int = 2,
) -> List[Dict]:
    """Search for hotels based on a natural language query."""
    search_results = hotels_vectordb.search(query, limit=limit)

    hotels = []
    for result in search_results:
        payload = result.payload
        hotels.append({
            "id": payload["id"],
            "name": payload["name"],
            "location": payload["location"],
            "price_tier": payload["price_tier"],
            "checkin_date": payload["checkin_date"],
            "checkout_date": payload["checkout_date"],
            "booked": payload["booked"],
            "chunk": payload["content"],
            "similarity": result.score,
        })
    return hotels

@tool
@humanloop_adapter.require_approval(execute_on_reject=False)
async def book_hotel(hotel_id: int, approval_result=None) -> str:
    """Book a hotel by its ID."""
    # If approval is rejected, this function body won't execute.
    # If approval is granted, approval_result will contain the approval details.
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 1 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully booked."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."

@tool
@humanloop_adapter.require_approval(execute_on_reject=False)
async def update_hotel(
    hotel_id: int,
    checkin_date: Optional[Union[datetime, date]] = None,
    checkout_date: Optional[Union[datetime, date]] = None,
    approval_result=None
) -> str:
    """Update a hotel's check-in and check-out dates by its ID and mark it as booked."""
    # If approval is rejected, this function body won't execute.
    # If approval is granted, approval_result will contain the approval details.
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Always mark the hotel as booked when updating
    cursor.execute("UPDATE hotels SET booked = 1 WHERE id = ?", (hotel_id,))

    if checkin_date:
        cursor.execute(
            "UPDATE hotels SET checkin_date = ? WHERE id = ?",
            (checkin_date.strftime('%Y-%m-%d'), hotel_id),
        )
    if checkout_date:
        cursor.execute(
            "UPDATE hotels SET checkout_date = ? WHERE id = ?",
            (checkout_date.strftime('%Y-%m-%d'), hotel_id),
        )

    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully updated and booked."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."

@tool
@humanloop_adapter.require_approval(execute_on_reject=False)
async def cancel_hotel(hotel_id: int, approval_result=None) -> str:
    """Cancel a hotel by its ID."""
    # If approval is rejected, this function body won't execute.
    # If approval is granted, approval_result will contain the approval details.
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 0 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"Hotel {hotel_id} successfully cancelled."
    else:
        conn.close()
        return f"No hotel found with ID {hotel_id}."
