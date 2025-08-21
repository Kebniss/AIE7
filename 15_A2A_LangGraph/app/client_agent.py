import asyncio
import logging
from typing import Any, List, TypedDict, Annotated
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Step 1: Implement the A2A Tool ---

async def _call_a2a_agent_async(query: str) -> str:
    """
    Asynchronously calls the A2A server agent with a given query.
    This function handles the core logic of setting up the client,
    sending the message, and parsing the response.
    """
    base_url = 'http://localhost:10000'
    logger.info(f"Connecting to A2A server at {base_url}...")

    try:
        # Set a longer timeout for potentially slow LLM responses
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0)) as httpx_client:
            # 1. Resolve the Agent Card to know how to communicate with the agent
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
            agent_card = await resolver.get_agent_card()
            logger.info("Successfully resolved agent card.")

            # 2. Initialize the A2A Client
            client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
            logger.info("A2AClient initialized.")

            # 3. Construct the message payload
            send_message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': query}],
                    'message_id': uuid4().hex,
                },
            }
            request = SendMessageRequest(
                id=str(uuid4()), params=MessageSendParams(**send_message_payload)
            )
            logger.info(f"Sending query: '{query}'")

            # 4. Send the message and await the response
            response = await client.send_message(request)
            logger.info("Received response from A2A server.")

            # 5. Extract the final text response by parsing the dictionary representation
            # This is more robust than relying on the Pydantic model's attributes directly
            try:
                response_dict = response.model_dump()
                final_text = response_dict["result"]["artifacts"][0]["parts"][0]["text"]
                logger.info(f"Successfully extracted response: '{final_text}'")
                return final_text
            except (KeyError, IndexError, TypeError) as e:
                logger.warning(f"Could not extract valid text from response. Error: {e}")
                logger.debug(f"Full response for debugging:\n{response.model_dump_json(indent=2)}")
                return "Error: Could not parse a valid response from the agent."

    except httpx.ConnectError as e:
        logger.error(f"Connection to A2A server failed. Is the server running? Error: {e}")
        return "Error: Could not connect to the A2A agent. Please ensure it is running."
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return f"An unexpected error occurred while communicating with the A2A agent: {e}"

@tool
def call_a2a_agent(query: str) -> str:
    """
    Use this tool to ask questions to a powerful AI assistant that has access to the web,
    academic papers, and local documents. It can answer complex questions about a wide
    variety of topics.
    """
    # This is a synchronous wrapper around the async function.
    # LangGraph tools are typically synchronous, so this makes it compatible.
    return asyncio.run(_call_a2a_agent_async(query))

# --- Step 2: Define the LangGraph Structure ---


# The state for our graph is a list of messages
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


# Initialize the LLM we want to use
# For this client agent, we can use a simple, fast model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Bind our A2A tool to the LLM
# This tells the LLM that it has access to this tool
llm_with_tools = llm.bind_tools([call_a2a_agent])


def agent_node(state: AgentState):
    """
    The primary node for our client agent.
    It invokes the LLM with the current state of the conversation and the available tools.
    The LLM's response, which could be a direct answer or a request to use a tool, is
    then returned to be added to the state.
    """
    print("\n---AGENT NODE---")
    print(f"MESSAGES: {state['messages']}")
    response = llm_with_tools.invoke(state["messages"])
    print(f"LLM RESPONSE: {response}")
    print("---END AGENT NODE---\n")
    # We return a list, because state updates are additive
    return {"messages": [response]}


# --- Step 3: Assemble the Graph ---

# Define the tool node. This is a pre-built node from LangGraph that executes
# the tools our agent decides to call.
tool_node = ToolNode([call_a2a_agent])


def should_continue(state: AgentState):
    """
    This is a routing function. It determines whether the agent should continue
    by calling a tool, or if it should finish the conversation.
    """
    print("\n---SHOULD CONTINUE---")
    last_message = state["messages"][-1]
    print(f"LAST MESSAGE: {last_message}")
    if getattr(last_message, "tool_calls", None):
        print("DECISION: Continue to action node")
        print("---END SHOULD CONTINUE---\n")
        return "continue"
    print("DECISION: End conversation")
    print("---END SHOULD CONTINUE---\n")
    return "end"


# Create a new StateGraph with our AgentState
workflow = StateGraph(AgentState)

# Add the agent node and the tool node to the graph
workflow.add_node("agent", agent_node)
workflow.add_node("action", tool_node)

# Set the entry point of the graph to the agent node
workflow.set_entry_point("agent")

# Add the conditional edge. This is the core logic of the graph.
# After the 'agent' node, it checks the 'should_continue' function.
# If it returns 'continue', it routes to the 'action' node.
# If it returns 'end', it finishes the graph.
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Add a normal edge from the action node back to the agent node.
# This means after a tool is called, the result is passed back to the agent
# so it can decide what to do next (e.g., respond to the user).
workflow.add_edge("action", "agent")

# Compile the graph into a runnable application
app = workflow.compile()

# --- Step 4: Add the Runner ---
if __name__ == "__main__":
    print("--- Client Agent Runner ---")
    print("Starting a conversation with the client agent...")
    
    # Ensure the main A2A server is running in a separate terminal
    # You can run it with `uv run python -m app`

    # Define the initial user query
    inputs = {"messages": [HumanMessage(content="Find me recent papers on transformer architectures")]}

    # Stream the results from the compiled graph
    print(f"\nUser Query: {inputs['messages'][0].content}")
    print("\nStreaming response from the agent...")
    print("-" * 30)

    final_response = None
    for output in app.stream(inputs):
        # The stream returns the full state at each step.
        # We're interested in the last message added to the state.
        for key, value in output.items():
            if key == "__end__":
                continue
            last_message = value["messages"][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                # This is a tool call, we can log it if we want
                print(f"Agent is calling tool: {last_message.tool_calls[0]['name']}")
            else:
                # This is the final response
                final_response = last_message.content
                print(f"Final Response: {final_response}")

    print("-" * 30)
    print("Conversation finished.")

