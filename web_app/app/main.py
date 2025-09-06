from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from pydantic import BaseModel
import uuid
import os
import sys

# Add the customer_support_chat directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from customer_support_chat.app.services.chat_service import process_user_message
from .core.user_data_manager import (
    get_user_session, 
    update_user_chat_history, 
    get_pending_action, 
    set_user_decision, 
    clear_pending_action, 
    clear_user_decision,
    get_operation_log
)

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

class ChatMessage(BaseModel):
    message: str

class ApprovalDecision(BaseModel):
    decision: str

def get_session_data(request: Request):
    """Get or create session data for the current user."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get the user session data
    session_data = get_user_session(session_id)
    
    # Ensure config exists in session_data
    if "config" not in session_data:
        session_data["config"] = {
            "thread_id": session_id,
            "passenger_id": "5102 899977"  # Default passenger ID
        }
    
    return {
        "session_id": session_id,
        "config": session_data["config"],
        "user_data": session_data
    }

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request, session_data: dict = Depends(get_session_data)):
    """Serve the chat interface."""
    # Set the session cookie
    response = templates.TemplateResponse("chat.html", {
        "request": request, 
        "session_id": session_data["session_id"],
        "chat_history": session_data["user_data"].get("chat_history", [])
    })
    response.set_cookie(key="session_id", value=session_data["session_id"])
    return response

@app.post("/chat")
async def chat(chat_message: ChatMessage, session_data: dict = Depends(get_session_data)):
    """Process a chat message and return the AI response."""
    try:
        # Process the user message
        ai_response = await process_user_message(session_data, chat_message.message)
        
        # Update the user's chat history
        update_user_chat_history(session_data["session_id"], chat_message.message, ai_response)
        
        # Return the AI response
        return JSONResponse(content={"response": ai_response})
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing chat message: {e}")
        # Return a user-friendly error message
        return JSONResponse(content={"error": "An unexpected error occurred. Please try again later."}, status_code=500)

# HITL (Human-in-the-Loop) endpoints

@app.get("/pending-action")
async def get_pending_action_endpoint(session_data: dict = Depends(get_session_data)):
    """Check if there is a pending action requiring user approval."""
    try:
        pending_action = get_pending_action(session_data["session_id"])
        if pending_action:
            return JSONResponse(content={"pending_action": pending_action})
        else:
            return JSONResponse(content={"pending_action": None})
    except Exception as e:
        print(f"Error checking pending action: {e}")
        return JSONResponse(content={"error": "An unexpected error occurred. Please try again later."}, status_code=500)


@app.post("/approve-action")
async def approve_action(request: Request, session_data: dict = Depends(get_session_data)):
    """Approve a pending action."""
    try:
        # Process the user's approval decision
        from customer_support_chat.app.services.chat_service import process_user_decision
        ai_response = await process_user_decision(session_data, "approve")
        
        # Update the user's chat history
        update_user_chat_history(session_data["session_id"], "[User approved action]", ai_response)
        
        # Return the AI response
        return JSONResponse(content={"response": ai_response})
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing approval: {e}")
        # Return a user-friendly error message
        return JSONResponse(content={"error": "An unexpected error occurred. Please try again later."}, status_code=500)


@app.post("/reject-action")
async def reject_action(request: Request, session_data: dict = Depends(get_session_data)):
    """Reject a pending action."""
    try:
        # Process the user's rejection decision
        from customer_support_chat.app.services.chat_service import process_user_decision
        ai_response = await process_user_decision(session_data, "reject")
        
        # Update the user's chat history
        update_user_chat_history(session_data["session_id"], "[User rejected action]", ai_response)
        
        # Return the AI response
        return JSONResponse(content={"response": ai_response})
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing rejection: {e}")
        # Return a user-friendly error message
        return JSONResponse(content={"error": "An unexpected error occurred. Please try again later."}, status_code=500)

@app.get("/operation-log")
async def get_operation_log_endpoint(session_data: dict = Depends(get_session_data)):
    """Get the operation log for the current session."""
    try:
        # Get only the most recent 20 log entries to reduce data transfer
        operation_log = get_operation_log(session_data["session_id"], limit=20)
        return JSONResponse(content={"operation_log": operation_log})
    except Exception as e:
        print(f"Error retrieving operation log: {e}")
        return JSONResponse(content={"error": "An unexpected error occurred. Please try again later."}, status_code=500)