import functools
import time
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_cohere import CohereRerank
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_core.messages import AIMessage, HumanMessage
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
    print(f"--- Starting {name} Node ---")
    t1 = time.time()
    result = agent.invoke(state)
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
    
    return {
        "messages": [
            HumanMessage(content=f"{name} agent responding:"),
            AIMessage(content=search_message, name=name)
        ]
    }

def writer_node(state: AgentState) -> AgentState:
    print("--- Starting Writer Node ---")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    writer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a writer. Use the provided context to answer the user's question clearly and accurately."
             "If the context is not enough, return 'I am not able to help'."),
            ("user", "Question: {question}\\n\\nContext:\\n{context}")
        ]
    )
    writer_chain = writer_prompt | llm | StrOutputParser()
    
    combined_context = ""
    for msg in state["messages"]:
        if isinstance(msg, AIMessage) and msg.name in ["Retrieval", "Search"]:
            combined_context += f"\\n{msg.content}\\n"
            
    question = state["messages"][0].content
    
    t1 = time.time()
    result = writer_chain.invoke({"question": question, "context": combined_context})
    t2 = time.time()
    print(f"--- Finished Writer Node in {t2 - t1:.2f}s ---")
    
    return {
        "messages": [
            HumanMessage(content="Writer agent responding:"),
            AIMessage(content=result, name="Writer")
        ]
    }

def router_node(state: AgentState, members) -> AgentState:
    print("--- Starting Router Node ---")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    router = create_router(
        llm,
        ("You are a supervisor tasked with managing a conversation between the"
         " following workers:  Search, Writer. Given the following user request,"
         " determine if the information is enough to answer the user query. If it is,"
         " pass the context to Writer. If it is not, pass the query to Search."
         " You should never ask Search to do anything beyond research."
         " You should never ask Writer to do anything beyond writing the answer given"
         " the context."),
        members,
    )
    
    t1 = time.time()
    result = router.invoke({"messages": state["messages"]})
    t2 = time.time()
    
    # Default to "Search" if the router fails to make a decision
    next_node = "Search"
    if result and isinstance(result, list) and len(result) > 0:
        try:
            # The router should choose between "Search" and "Writer"
            if result[0]["args"]["next"] in members:
                next_node = result[0]["args"]["next"]
            else:
                # This case handles if the LLM hallucinates an invalid member
                print(f"--- Router returned invalid member '{result[0]['args']['next']}', defaulting to Search. ---")
        except (KeyError, TypeError, IndexError) as e:
            print(f"--- Router failed to parse result, defaulting to Search. Error: {e} ---")

    print(f"--- Router decision: {next_node} in {t2 - t1:.2f}s ---")
    return {
        "next": next_node
    }
