import glob
import time
import functools
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    retrieve_node,
    writer_node,
    router_node,
    create_search_agent_node,
)

def load_documents_and_create_retriever(data_dir="./data"):
    pdf_files = glob.glob(f"{data_dir}/*.pdf")
    all_documents = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            pages = loader.load()
            documents = text_splitter.split_documents(pages)
            all_documents.extend(documents)
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
            
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Qdrant.from_documents(
        all_documents,
        embeddings,
        location=":memory:",
        collection_name="Manuals"
    )
    
    naive_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    compressor = CohereRerank(model="rerank-v3.5")
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=naive_retriever
    )
    
    return compression_retriever

def create_graph():
    retriever = load_documents_and_create_retriever()
    search_node = create_search_agent_node()
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("Retrieve", functools.partial(retrieve_node, retriever=retriever))
    graph.add_node("Writer", writer_node)
    graph.add_node("Search", search_node)
    graph.add_node("Router", functools.partial(router_node, members=["Search", "Writer"]))
    
    # Set entry point
    graph.set_entry_point("Retrieve")
    
    # Add edges
    graph.add_edge("Retrieve", "Router")
    graph.add_conditional_edges(
        "Router",
        lambda x: x["next"],
        {
            "Search": "Search",
            "Writer": "Writer",
            "FINISH": END
        },
    )
    graph.add_edge("Search", "Writer")
    graph.add_edge("Writer", END)
    
    # Compile the graph
    return graph.compile()
