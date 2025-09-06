# customer_support_chat/app/services/assistants/blog_search_assistant.py

from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from customer_support_chat.app.services.tools.blog import search_blog_posts
from customer_support_chat.app.services.assistants.assistant_base import Assistant, llm, CompleteOrEscalate
from pydantic import BaseModel, Field

# Define task delegation tool for Blog Search
class ToBlogSearch(BaseModel):
    """Transfers work to a specialized assistant to handle blog post searches."""
    keyword: str = Field(description="The keyword to search for in blog posts.")

# Blog search assistant prompt
blog_search_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized assistant for searching blog posts. "
            "Your primary role is to use the search_blog_posts tool to find relevant articles based on user keywords. "
            "Present the search results in a clear and readable format, showing title, excerpt, and link. "
            "If the user's request is not related to blog search, "
            "use the CompleteOrEscalate tool to return control to the main assistant. "
            "Current time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# Blog search assistant tools
blog_search_assistant_tools = [
    search_blog_posts,
    CompleteOrEscalate,
]

# Create the blog search assistant runnable
blog_search_assistant_runnable = blog_search_assistant_prompt | llm.bind_tools(blog_search_assistant_tools)

# Instantiate the blog search assistant
blog_search_assistant = Assistant(blog_search_assistant_runnable)