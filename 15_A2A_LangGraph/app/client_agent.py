import asyncio
import logging
from typing import Any, List, TypedDict
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

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

            # 5. Extract the final text response from the complex response object
            # The correct path to the text is result -> artifacts -> parts -> text
            if (
                response.root
                and response.root.result
                and response.root.result.artifacts
                and response.root.result.artifacts[0].parts
            ):
                final_text = response.root.result.artifacts[0].parts[0].text
                logger.info(f"Successfully extracted response: '{final_text}'")
                return final_text

            logger.warning("Could not extract a valid text response from the server's reply.")
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
    messages: List[BaseMessage]


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
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# --- We will add Step 3 (Assemble the Graph) and Step 4 (Runner) below this line ---

