<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 14: Build & Serve Agentic Graphs with LangGraph</h1>

| 🤓 Pre-work | 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| – | – | – | – | You are here! | – | – |

# Build 🏗️

Run the repository and complete the following:

- 🤝 Breakout Room Part #1 — Building and serving your LangGraph Agent Graph
  - Task 1: Getting Dependencies & Environment
    - Configure `.env` (OpenAI, Tavily, optional LangSmith)
  - Task 2: Serve the Graph Locally
    - `uv run langgraph dev` (API on http://localhost:2024)
  - Task 3: Call the API
    - `uv run test_served_graph.py` (sync SDK example)
  - Task 4: Explore assistants (from `langgraph.json`)
    - `agent` → `simple_agent` (tool-using agent)
    - `agent_helpful` → `agent_with_helpfulness` (separate helpfulness node)

- 🤝 Breakout Room Part #2 — Using LangGraph Studio to visualize the graph
  - Task 1: Open Studio while the server is running
    - https://smith.langchain.com/studio?baseUrl=http://localhost:2024
  - Task 2: Visualize & Stream
    - Start a run and observe node-by-node updates
  - Task 3: Compare Flows
    - Contrast `agent` vs `agent_helpful` (tool calls vs helpfulness decision)

<details>
<summary>🚧 Advanced Build 🚧 (OPTIONAL - <i>open this section for the requirements</i>)</summary>

- Create and deploy a locally hosted MCP server with FastMCP.
- Extend your tools in `tools.py` to allow your LangGraph to consume the MCP Server.
</details>

# Ship 🚢

- Running local server (`langgraph dev`)
- Short demo showing both assistants responding

# Share 🚀
- Walk through your graph in Studio
- Share 3 lessons learned and 3 lessons not learned


#### ❓ Question:

What is the purpose of the `chunk_overlap` parameter when using `RecursiveCharacterTextSplitter` to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?

Answer: 

The overlap is used to ensure that semantically related information is not split across different chunks which could make it difficult for the retrieval to fetch the most relevant information for a given query. 

A larger overlap ensures more continuity bewteen chunks, useful for documents with complex sentence structure or dense flow of ideas as it minimizes the risk of losing important contextual information. This strategy makes the retrieval more restistant to bad splits and leads to more comprehensive embeddings because each chunk has more context. The drawbacks of this strategy include the followings: this strategy increases redundancy of embeddings because the same string pieces are stored in multiple chunks, it increases the number of embeddings to store so retrieval latency is higher and most importantly chunks might end up containing multiple semantic blocks reducing the effectiveness of retrieval.

A smaller overlap means reduced redundancy and storage costs, making the retrieval process faster. However, this comes at the risk of losing crucial context, as important sentences or ideas may be split across chunks, leading to less accurate embeddings and a lower overall retrieval performance.

#### ❓ Question:

Your retriever is configured with `search_kwargs={"k": 5}`. How would adjusting `k` likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?

Answer: 

Adjusting the k value in a retriever creates a direct trade-off between RAGAS metrics for Context Recall and Context Precision. Increasing k (the number of documents retrieved) will likely improve Context Recall by making it more probable that all necessary information is found, but it will simultaneously decrease Context Precision by including more irrelevant, or "noisy," documents. Conversely, decreasing k will likely increase Context Precision by focusing on only the most relevant documents, but this will reduce Context Recall as there's a higher risk of missing key information needed for a complete answer. The ideal k value balances this trade-off based on whether the application prioritizes a comprehensive or a concise and highly-relevant context.

#### ❓ Question:

Compare the `agent` and `agent_helpful` assistants defined in `langgraph.json`. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

Answer:

The agent and agent_helpful assistants differ in their termination logic. The simple agent terminates immediately when no tool calls are made, while agent_helpful adds a helpfulness evaluator that runs after the agent's final response. This evaluator compares the initial query to the final response and makes a binary decision: if helpful (Y), the graph terminates; if unhelpful (N), execution routes back to the agent for improvement. The helpfulness evaluator acts as a quality gate, ensuring the agent only terminates with genuinely helpful responses rather than potentially incomplete or unsatisfactory answers.
