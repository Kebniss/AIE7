import logging
import functools
import time
from typing import TypedDict, List, Annotated, Optional, Dict, Any
import operator

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_cohere import CohereRerank
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from .state import AgentState
from .tools import search_internet

# Helper functions
def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    """Create a function-calling agent and add it to the graph."""
    system_prompt += (
        "\\nWork autonomously according to your specialty, using the tools available to you."
        " Do not ask for clarification."
        " Your other team members (and other teams) will collaborate with you with their own specialties."
        " You are chosen for a reason!"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def create_router(llm: ChatOpenAI, system_prompt, members):
    """An LLM-based router."""
    options = members
    
    tool_def = {
        "type": "function",
        "function": {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "next": {
                        "type": "string",
                        "enum": options,
                    },
                },
                "required": ["next"],
            },
        }
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                "Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), team_members=", ".join(members))
    
    return (
        prompt
        | llm.bind_tools([tool_def], tool_choice={"type": "function", "function": {"name": "route"}})
        | JsonOutputToolsParser()
    )

def create_search_agent_node():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    search_agent = create_agent(
        llm, 
        [search_internet], 
        "You are a research assistant who can search for details to answer the user query."
    )
    return functools.partial(search_agent_node, agent=search_agent, name="Search")

# Agent Nodes
def retrieve_node(state: AgentState, retriever) -> AgentState:
    print("--- Starting Retrieval Node ---")
    question = state["messages"][-1].content
    
    print(f"Retrieving documents for question: {question}")
    t1 = time.time()
    retrieved_docs = retriever.invoke(question)
    t2 = time.time()
    print(f"--- Finished Retrieving Documents in {t2 - t1:.2f}s ---")
    
    context_message = "Retrieved context from documents:\\n"
    for i, doc in enumerate(retrieved_docs):
        context_message += f"\\n--- Document {i+1} ---\\n{doc.page_content}\\n"
    
    print("--- Finished Retrieval Node ---")
    return {
        "messages": [
            HumanMessage(content="Retrieval agent responding:"),
            AIMessage(content=context_message, name="Retrieval")
        ]
    }

def search_agent_node(state: AgentState, agent, name: str) -> AgentState:
    iteration = state.get("iteration_count", 0)
    print(f"=== ITERATION {iteration} - SEARCH NODE ===")
    print(f"Previous context size: {len(state.get('search_context', []))}")
    print(f"Total messages in state: {len(state['messages'])}")
    
    t1 = time.time()
    try:
        result = agent.invoke(state)
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return {
            "messages": [
                HumanMessage(content=f"{name} agent responding:"),
                AIMessage(content=f"Search failed: {str(e)}. Proceeding with available information.", name=name)
            ],
            "should_continue": False  # Stop on search failure
        }
    t2 = time.time()
    print(f"--- Finished {name} Node in {t2 - t1:.2f}s ---")
    
    if isinstance(result, dict):
        output_text = result.get('output', str(result))
        if hasattr(result.get('output'), '__iter__') and all(hasattr(item, 'page_content') for item in result.get('output')):
            search_message = "Internet search results:\\n"
            for i, doc in enumerate(result.get('output')):
                search_message += f"\\n--- Result {i+1} ---\\n{doc.page_content}\\n"
        else:
            search_message = output_text
    else:
        search_message = str(result)
    
    print(f"=== SEARCH COMPLETE - Found {len(search_message)} results ===")
    return {
        "messages": [
            HumanMessage(content=f"{name} agent responding:"),
            AIMessage(content=search_message, name=name)
        ],
        "search_context": state.get("search_context", []) + [search_message],
        "debug_info": {
            "iteration": iteration,
            "search_results_count": len(search_message),
            "context_size": len(search_message)
        }
    }

def writer_node(state: AgentState) -> AgentState:
    print("--- Starting Writer Node ---")
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    except Exception as e:
        logging.error(f"Error creating ChatOpenAI in writer_node: {e}")
        raise
    
    # Determine information sources
    has_manual_context = any(
        isinstance(msg, AIMessage) and msg.name == "Retrieval" 
        for msg in state["messages"]
    )
    has_search_context = any(
        isinstance(msg, AIMessage) and msg.name == "Search" 
        for msg in state["messages"]
    )
    
    # Create source attribution message
    source_info = ""
    if has_manual_context and has_search_context:
        source_info = "I found information from both the manuals and internet research."
    elif has_manual_context:
        source_info = "I found this information in the manuals."
    elif has_search_context:
        source_info = "I couldn't find the answer in the manuals, but I found this information on the internet."
    else:
        source_info = "I don't have enough information to answer your question."
    
    writer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a writer. Use the provided context to answer the user's question clearly and accurately."
             "If the context is not enough, return 'I am not able to help'."
             "Always start your response with a brief statement about your information sources."),
            ("user", "Question: {question}\\n\\nContext:\\n{context}\\n\\nSource Attribution: {source_info}")
        ]
    )
    writer_chain = writer_prompt | llm
    
    combined_context = ""
    for msg in state["messages"]:
        if isinstance(msg, AIMessage) and msg.name in ["Retrieval", "Search"]:
            combined_context += f"\\n{msg.content}\\n"
            
    question = state["messages"][0].content
    
    t1 = time.time()
    result = writer_chain.invoke({
        "question": question, 
        "context": combined_context,
        "source_info": source_info
    })
    t2 = time.time()
    print(f"--- Writer node generated response: {result} ---")
    print(f"--- Finished Writer Node in {t2 - t1:.2f}s ---")
    
    # Extract the content from the result
    if hasattr(result, 'content'):
        content = result.content
    else:
        content = str(result)
    
    return {
        "messages": [
            HumanMessage(content="Writer agent responding:"),
            AIMessage(content=content, name="Writer")
        ]
    }

def router_node(state: AgentState, members) -> AgentState:
    iteration = state.get("iteration_count", 0)
    should_continue = state.get("should_continue", True)
    
    print(f"=== ROUTER DECISION - ITERATION {iteration} ===")
    print(f"Should continue from writer: {should_continue}")
    print(f"Current iteration: {iteration}")
    
    # Force stop at iteration 3
    if iteration >= 3:
        print("=== MAX ITERATIONS REACHED (3) - STOPPING ===")
        return {"next": "Writer"}
    
    # Check writer's assessment
    if not should_continue:
        print("=== WRITER ASSESSMENT: STOP - RESPONSE COMPLETE ===")
        return {"next": "Writer"}
    
    print("=== CONTINUING TO SEARCH ===")
    return {"next": "Search"}

def manage_context(state: AgentState) -> AgentState:
    """Manage context to prevent token overflow"""
    search_context = state.get("search_context", [])
    total_context_length = sum(len(ctx) for ctx in search_context)
    
    print(f"=== CONTEXT MANAGEMENT ===")
    print(f"Total context length: {total_context_length} characters")
    print(f"Number of search contexts: {len(search_context)}")
    
    # If context is getting too large, keep only recent searches
    if total_context_length > 10000:  # Conservative limit
        print("Context too large, keeping only recent searches")
        search_context = search_context[-2:]  # Keep last 2 searches
    
    return {"search_context": search_context}

def increment_iteration(state: AgentState) -> AgentState:
    current_count = state.get("iteration_count", 0)
    new_count = current_count + 1
    print(f"=== INCREMENTING ITERATION: {current_count} -> {new_count} ===")
    return {"iteration_count": new_count}

def log_state_info(state: AgentState, node_name: str):
    """Comprehensive state logging"""
    print(f"\n=== {node_name} STATE INFO ===")
    print(f"Iteration: {state.get('iteration_count', 0)}")
    print(f"Messages count: {len(state['messages'])}")
    print(f"Search contexts: {len(state.get('search_context', []))}")
    print(f"Should continue: {state.get('should_continue', True)}")
    if 'debug_info' in state:
        print(f"Debug info: {state['debug_info']}")
    print("=" * 50)
