from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .graph.builder import create_graph
from .schemas import InvokeRequest
from langchain_core.messages import HumanMessage
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the graph on startup
    print("Loading graph...")
    app.state.graph = create_graph()
    print("Graph loaded successfully.")
    yield
    # Clean up resources if needed on shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_generator(graph, input_message: str):
    async for chunk in graph.astream(
        {"messages": [HumanMessage(content=input_message)]},
        config={"recursion_limit": 100},
    ):
        # We only want to stream the final output from the writer node
        if "Writer" in chunk:
            delta = chunk["Writer"]["messages"][-1].content
            if delta:
                # Stream each delta as it arrives (like the reference app)
                yield f"data: {delta}\n\n"

@app.post("/invoke")
async def invoke(request: InvokeRequest):
    graph = app.state.graph
    return StreamingResponse(stream_generator(graph, request.input), media_type="text/event-stream")

def start():
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
