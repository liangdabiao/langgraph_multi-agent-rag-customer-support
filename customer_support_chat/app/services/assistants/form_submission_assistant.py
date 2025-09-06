# customer_support_chat/app/services/assistants/form_submission_assistant.py

from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from customer_support_chat.app.services.tools.forms import submit_form
from customer_support_chat.app.services.assistants.assistant_base import Assistant, llm, CompleteOrEscalate
from pydantic import BaseModel, Field
from typing import Dict, Any

# Define task delegation tool for Form Submission
class ToFormSubmission(BaseModel):
    """Transfers work to a specialized assistant to handle user form submissions."""
    form_data: Dict[str, Any] = Field(description="A dictionary containing form field names as keys and user inputs as values.")

# Form submission assistant prompt
form_submission_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized assistant for handling user form submissions. "
            "Your primary role is to collect necessary information from the user and then use the submit_form tool "
            "to send the data to the specified API endpoint. "
            "The form requires the following mandatory fields: "
            "- 'your-name': The user's full name "
            "- 'your-email': The user's email address "
            "- 'your-subject': The subject of the inquiry "
            "Additionally, the form always includes '_wpcf7': 942 as a fixed parameter. "
            "You MUST collect all three mandatory fields from the user before submitting the form. "
            "If the user doesn't provide all required information, politely ask for the missing fields. "
            "Always confirm with the user before submitting the form. "
            "If the user's request is not related to form submission, "
            "use the CompleteOrEscalate tool to return control to the main assistant. "
            "For debugging purposes, please include detailed information about the form data being submitted. "
            "Current time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# Form submission assistant tools
form_submission_assistant_tools = [
    submit_form,
    CompleteOrEscalate,
]

# Create the form submission assistant runnable
form_submission_assistant_runnable = form_submission_assistant_prompt | llm.bind_tools(form_submission_assistant_tools)

# Instantiate the form submission assistant
form_submission_assistant = Assistant(form_submission_assistant_runnable)