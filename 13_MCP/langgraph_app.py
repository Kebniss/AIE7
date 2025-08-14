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

# Initialize the MCP toolkit to connect to your server
mcp_toolkit = MCPToolkit(
    server_name="mcp-server",
    command="uv",
    args=["--directory", "/Users/ludovicagonella/code/AIE7/13_MCP", "run", "server.py"]
)

# Get the tools from your MCP server
mcp_tools = mcp_toolkit.get_tools()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Bind the MCP tools to the LLM
llm_with_tools = llm.bind_tools(mcp_tools)

# Define the state structure
class AgentState(TypedDict):
    messages: Annotated[list, "The messages in the conversation"]
    current_task: Annotated[str, "The current task being processed"]

# Define the agent function
def agent(state: AgentState) -> AgentState:
    """Agent that processes the current task using MCP tools"""
    messages = state["messages"]
    current_task = state["current_task"]
    
    # Add the current task as a human message
    messages.append(HumanMessage(content=current_task))
    
    # Get response from LLM with tools
    response = llm_with_tools.invoke(messages)
    
    # Add the AI response
    messages.append(response)
    
    return {
        "messages": messages,
        "current_task": current_task
    }

# Create the workflow
workflow = StateGraph(AgentState)

# Add the agent node
workflow.add_node("agent", agent)

# Set the entry point
workflow.set_entry_point("agent")

# Set the end point
workflow.add_edge("agent", END)

# Compile the workflow
app = workflow.compile()

# Example usage functions
async def run_workflow(task: str):
    """Run the workflow with a given task"""
    result = await app.ainvoke({
        "messages": [],
        "current_task": task
    })
    return result

def run_workflow_sync(task: str):
    """Run the workflow synchronously with a given task"""
    result = app.invoke({
        "messages": [],
        "current_task": task
    })
    return result

# Main execution
if __name__ == "__main__":
    # Example tasks that will use your MCP tools
    example_tasks = [
        "Search for information about artificial intelligence and then roll a 20-sided die",
        "Generate a secure password with 16 characters including symbols and numbers",
        "Search for the latest news about machine learning and roll 3 six-sided dice"
    ]
    
    print("🤖 LangGraph MCP Integration Demo")
    print("=" * 50)
    
    for i, task in enumerate(example_tasks, 1):
        print(f"\n📋 Task {i}: {task}")
        print("-" * 30)
        
        try:
            # Run the workflow
            result = run_workflow_sync(task)
            
            # Display the result
            print("✅ Result:")
            for message in result["messages"]:
                if isinstance(message, AIMessage):
                    print(f"🤖 AI: {message.content}")
                elif isinstance(message, HumanMessage):
                    print(f"👤 Human: {message.content}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)
    
    print("\n🎉 Demo completed! Your MCP server is working with LangGraph!") 