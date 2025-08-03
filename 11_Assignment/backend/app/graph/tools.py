from typing import Annotated
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

__all__ = ["tool_belt", "search_internet"]

# You can add other tools here as well.
tavily_tool = TavilySearchResults(max_results=5)

@tool
def search_internet(query: Annotated[str, "Query to search the internet for"]):
    """Search the internet for additional information"""
    # Use your existing tavily_tool
    results = tavily_tool.invoke(query)
    
    # Convert results to Document format
    docs = []
    for result in results:
        content = f"Title: {result.get('title', '')}\\nContent: {result.get('content', '')}\\nURL: {result.get('url', '')}"
        docs.append(Document(page_content=content, metadata={"source": "internet_search", "url": result.get('url', '')}))
    
    return docs

tool_belt = [
    search_internet,
]
