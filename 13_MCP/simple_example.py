import asyncio
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters import MCPToolkit
from langgraph import StateGraph, END
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def simple_mcp_integration():
    """Simple example of using MCP tools with LangChain"""
    
    # Initialize the MCP toolkit
    mcp_toolkit = MCPToolkit(
        server_name="mcp-server",
        command="uv",
        args=["--directory", "/Users/ludovicagonella/code/AIE7/13_MCP", "run", "server.py"]
    )
    
    # Get the tools
    tools = mcp_toolkit.get_tools()
    
    print("🔧 Available MCP Tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Test a simple interaction
    test_message = "Generate a password and then search for information about cybersecurity"
    
    print(f"\n🧪 Testing with: {test_message}")
    print("-" * 40)
    
    try:
        response = llm_with_tools.invoke(test_message)
        print("✅ Response:")
        print(response.content)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_mcp_integration()