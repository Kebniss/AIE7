"""LangGraph agent integration with production features."""

from typing import Dict, Any, List, Optional
import os

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_core.tools import tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

from .models import get_openai_model
from .rag import ProductionRAGChain


class AgentState(TypedDict):
    """State schema for agent graphs."""
    messages: Annotated[List[BaseMessage], add_messages]


def create_rag_tool(rag_chain: ProductionRAGChain):
    """Create a RAG tool from a ProductionRAGChain."""
    
    @tool
    def retrieve_information(query: str) -> str:
        """Use Retrieval Augmented Generation to retrieve information from the student loan documents."""
        try:
            result = rag_chain.invoke(query)
            return result.content if hasattr(result, 'content') else str(result)
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
    
    return retrieve_information


def get_default_tools(rag_chain: Optional[ProductionRAGChain] = None) -> List:
    """Get default tools for the agent.
    
    Args:
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        List of tools
    """
    tools = []
    
    # Add Tavily search if API key is available
    if os.getenv("TAVILY_API_KEY"):
        tools.append(TavilySearchResults(max_results=5))
    
    # Add Arxiv tool
    tools.append(ArxivQueryRun())
    
    # Add RAG tool if provided
    if rag_chain:
        tools.append(create_rag_tool(rag_chain))
    
    return tools


def create_langgraph_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None
):
    """Create a simple LangGraph agent.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        Compiled LangGraph agent
    """
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)
    
    def call_model(state: AgentState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState):
        """Route to tools if the last message has tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        return END
    
    # Build graph
    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)
    
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"action": "action", END: END})
    graph.add_edge("action", "agent")
    
    return graph.compile()

def create_helpful_langgraph_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None
):
    """
    Create a LangGraph agent with helpfulness verification.
    
    This agent adds a helpfulness check node that evaluates whether the response
    adequately addresses the user's query and allows the agent to refine it if necessary.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        Compiled LangGraph agent with helpfulness verification
    """
    if tools is None:
        tools = get_default_tools(rag_chain)
    
    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(temperature=temperature)
    
    # Create helpfulness evaluation model (can use same model or different one)
    helpfulness_model = get_openai_model(model_name=model_name, temperature=0.1)
    
    def call_model(state: AgentState) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState):
        """Route to tools if the last message has tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        return "helpfulness_check"
    
    def check_helpfulness(state: AgentState) -> Dict[str, Any]:
        """
        Check if the agent's response is helpful and route for refinement if necessary.
        """
        messages = state["messages"]
        
        # Get the user's original question and the agent's response
        user_question = None
        agent_response = None
        
        for msg in messages:
            if hasattr(msg, 'content') and msg.content:
                if user_question is None:
                    user_question = msg.content
                elif agent_response is None and hasattr(msg, 'tool_calls') is False:
                    agent_response = msg.content
        
        # If we can't find the components, just return the current state
        if not user_question or not agent_response:
            return {"messages": [AIMessage(content="I apologize, but I couldn't process your request properly.")]}
        
        # Create helpfulness evaluation prompt
        helpfulness_prompt = f"""
        You are a helpfulness evaluator. Your job is to determine if the given response adequately addresses the user's question.

        USER QUESTION: {user_question}

        AGENT RESPONSE: {agent_response}

        Evaluate the response on a scale of 1-10 where:
        1 = Completely unhelpful, doesn't address the question
        5 = Somewhat helpful, partially addresses the question  
        10 = Very helpful, fully addresses the question

        Consider:
        - Does the response directly answer the question asked?
        - Is the information accurate and relevant?
        - Is the response clear and understandable?
        - Does it provide actionable information if applicable?

        Respond with ONLY a number from 1-10, followed by a brief explanation.
        """
        
        # Evaluate helpfulness
        evaluation = helpfulness_model.invoke(helpfulness_prompt)
        evaluation_text = evaluation.content if hasattr(evaluation, 'content') else str(evaluation)
        
        # Extract score (look for first number 1-10)
        import re
        score_match = re.search(r'(\d+)', evaluation_text)
        score = int(score_match.group(1)) if score_match else 5
        
        # If score is low (≤6), route back to agent for refinement
        if score <= 6:
            # Add a refinement instruction to the state
            refinement_message = AIMessage(content=f"""
            The previous response was not helpful enough (score: {score}/10). 
            Please provide a more helpful, accurate, and comprehensive response to: "{user_question}"
            
            Consider using the available tools to gather better information if needed.
            """)
            return {"messages": [refinement_message]}
        else:
            # Response is helpful enough, end here
            return {"messages": [AIMessage(content=agent_response)]}
    
    def should_refine(state: AgentState):
        """Route based on whether refinement is needed."""
        last_message = state["messages"][-1]
        
        # Check if this is a refinement instruction
        if hasattr(last_message, 'content') and "not helpful enough" in last_message.content:
            return "agent"  # Route back to agent for refinement
        else:
            return END  # End the conversation
    
    # Build graph
    graph = StateGraph(AgentState)
    tool_node = ToolNode(tools)
    
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.add_node("helpfulness_check", check_helpfulness)
    
    graph.set_entry_point("agent")
    
    # Add conditional edges
    graph.add_conditional_edges("agent", should_continue, {"action": "action", "helpfulness_check": "helpfulness_check"})
    graph.add_edge("action", "agent")
    
    # Add conditional edge from helpfulness check
    graph.add_conditional_edges("helpfulness_check", should_refine, {"agent": "agent", END: END})
    
    return graph.compile()
