from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from customer_support_chat.app.services.tools import (
    search_hotels,
    book_hotel,
    update_hotel,
    cancel_hotel,
)
from customer_support_chat.app.services.assistants.assistant_base import Assistant, CompleteOrEscalate, llm

# Hotel booking assistant prompt
hotel_booking_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized assistant for handling hotel bookings, modifications, and cancellations. "
            "The primary assistant delegates work to you whenever the user needs help with hotel-related operations. "
            "You can search for available hotels, book hotels, update existing bookings, and cancel bookings based on the user's requests. "
            "When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "\n\nFor cancellation requests:\n"
            "- When the user says 'cancel it', 'cancel my booking', etc., look at the conversation history to identify which hotel they're referring to.\n"
            "- If a hotel was recently booked or mentioned, use that hotel's ID for the cancellation.\n"
            "- Always use the cancel_hotel tool for cancellation requests - do NOT just provide a text response.\n"
            "- The cancel_hotel tool requires a hotel_id parameter.\n"
            "\n\nFor booking modifications (like changing dates), use the update_hotel tool. "
            "If you need more information or the customer changes their mind, escalate the task back to the main assistant. "
            "Remember that operations (booking, updating, cancelling) aren't completed until after the relevant tool has successfully been used."
            "\nCurrent time: {time}."
            '\n\nIf the user needs help, and none of your tools are appropriate for it, then "CompleteOrEscalate" the dialog to the host assistant.'
            " Do not waste the user's time. Do not make up invalid tools or functions."
            "\n\nSome examples for which you should CompleteOrEscalate:\n"
            " - 'what's the weather like this time of year?'\n"
            " - 'nevermind I think I'll book separately'\n"
            " - 'I need to figure out transportation while I'm there'\n"
            " - 'Oh wait I haven't booked my flight yet I'll do that first'\n"
            " - 'Hotel booking confirmed'\n\n"
            "Examples for when to use cancel_hotel tool (ALWAYS use the tool, never just text response):\n"
            " - 'cancel it' (when referring to an existing booking) → call cancel_hotel with the hotel_id\n"
            " - 'cancel my hotel booking' → call cancel_hotel with the hotel_id\n"
            " - 'I want to cancel the reservation' → call cancel_hotel with the hotel_id\n"
            " - 'please cancel my hotel' → call cancel_hotel with the hotel_id\n"
            "You should identify the hotel ID from the conversation context when cancelling. "
            "If the hotel ID is not clear from context, ask the user to clarify which hotel to cancel.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# Hotel booking tools
book_hotel_safe_tools = [search_hotels, CompleteOrEscalate]
book_hotel_sensitive_tools = [book_hotel, update_hotel, cancel_hotel]
book_hotel_tools = book_hotel_safe_tools + book_hotel_sensitive_tools

# Create the hotel booking assistant runnable
book_hotel_runnable = hotel_booking_prompt | llm.bind_tools(
    book_hotel_tools
)

# Instantiate the hotel booking assistant
hotel_booking_assistant = Assistant(book_hotel_runnable)