from vectorizer.app.vectordb.vectordb import VectorDB
from customer_support_chat.app.core.settings import get_settings
from langchain_core.tools import tool
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

settings = get_settings()
faq_vectordb = VectorDB(table_name="faq", collection_name="faq_collection")

@tool
def search_faq(
    query: str,
    limit: int = 2,
) -> List[Dict]:
    """Search for FAQ entries based on a natural language query."""
    search_results = faq_vectordb.search(query, limit=limit)

    faq_entries = []
    for result in search_results:
        payload = result.payload
        content = payload.get("content", "")
        
        # Try to parse Q&A from content if it follows the numbered Q&A format
        question = "General FAQ Information"
        answer = content
        category = "FAQ"
        
        # Look for numbered question pattern (e.g., "1. Can I receive...")
        import re
        question_match = re.search(r'^\d+\. (.+?)(?=\n|$)', content, re.MULTILINE)
        if question_match:
            question = question_match.group(1).strip()
            # Extract answer (everything after the question)
            answer_start = content.find(question) + len(question)
            answer = content[answer_start:].strip()
        elif content.startswith('##'):
            # Handle section headers
            lines = content.split('\n', 1)
            question = lines[0].replace('##', '').strip()
            answer = lines[1] if len(lines) > 1 else "See section content for details."
        
        faq_entries.append({
            "question": question,
            "answer": answer,
            "category": category,
            "chunk": content,
            "similarity": result.score,
        })
    return faq_entries

@tool
def lookup_policy(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes or performing other 'write' events."""
    faq_results = search_faq.invoke({"query": query, "limit": 2})
    if not faq_results:
        return "Sorry, I couldn't find any relevant policy information. Please contact support for assistance."
    
    policy_info = "\n\n".join([f"Q: {entry['question']}\nA: {entry['answer']}" for entry in faq_results])
    return f"Here's the relevant policy information:\n\n{policy_info}"
