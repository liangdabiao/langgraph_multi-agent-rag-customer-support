# customer_support_chat/app/services/tools/forms.py

import httpx
from langchain_core.tools import tool
from customer_support_chat.app.core.settings import get_settings
from typing import Dict, Any

settings = get_settings()

@tool
def submit_form(form_data: Dict[str, Any]) -> str:
    """Submit user form data to a specified API.
    
    Args:
        form_data: A dictionary containing form field names as keys and user inputs as values.
                   Must include the following mandatory fields: 'your-name', 'your-email', 'your-subject'.
        
    Returns:
        A confirmation message or error message from the API.
    """
    if not settings.FORM_SUBMISSION_API_URL:
        raise ValueError("Form submission API URL is not configured.")
    
    # Validate required fields
    required_fields = ['your-name', 'your-email', 'your-subject']
    missing_fields = [field for field in required_fields if field not in form_data or not form_data[field]]
    
    if missing_fields:
        raise ValueError(f"Missing required form fields: {', '.join(missing_fields)}")
    
    # Add fixed _wpcf7 parameter
    final_form_data = form_data.copy()
    final_form_data["_wpcf7"] = 946
    
    with httpx.Client() as client:
        try:
            response = client.post(
                settings.FORM_SUBMISSION_API_URL,
                json=final_form_data
            )
            
            # Log detailed response information for debugging
            print(f"Form submission API response status: {response.status_code}")
            print(f"Form submission API response headers: {dict(response.headers)}")
            
            try:
                result = response.json()
                print(f"Form submission API response JSON: {result}")
            except Exception as json_error:
                print(f"Form submission API response text (non-JSON): {response.text}")
                result = {}
            
            response.raise_for_status()
            
            # Return a success message or specific response from the API
            # This might need adjustment based on the actual API response format
            if result.get("status") == "success" or response.status_code == 200:
                return f"Form submitted successfully. Thank you for your submission!"
            else:
                return f"Form submission may have encountered an issue. API response: {result}"
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error occurred while submitting form: {e}")
        except Exception as e:
            raise Exception(f"An error occurred while submitting form: {e}")