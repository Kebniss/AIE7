from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .graph.builder import create_graph
from .schemas import InvokeRequest
from langchain_core.messages import HumanMessage
import uvicorn


# Create the FastAPI app
app = FastAPI()

# Create the graph
graph = create_graph()

# Define the stream for the response
async def stream_generator(input_message: str):
    async for chunk in graph.astream(
        {"messages": [HumanMessage(content=input_message)]},
        config={"recursion_limit": 100},
    ):
        if "__end__" not in chunk:
            for key, value in chunk.items():
                yield f"data: {value['messages'][-1].content}\\n\\n"

@app.post("/invoke")
async def invoke(request: InvokeRequest):
    return StreamingResponse(stream_generator(request.input), media_type="text/event-stream")

def start():
    """Start the FastAPI server."""
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
