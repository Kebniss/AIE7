# ManualAIze - Certification Report

📹 **[Watch the Application Walkthrough](https://www.loom.com/share/38c8f65afaab4c23bd64406c248c7d13?sid=8e2f5036-dc34-47ad-9294-dbca44c13294)**

## Task 1

### Problem
Customers often lose or ignore physical product manuals, resulting in wasted time and difficulty when they need to troubleshoot a product issue.

### User
The user for this solution is a consumer who has purchased a product with an instruction manual. This person is often motivated to get the item working quickly and intuitively, which is why they tend to skip reading the manual. They might be able to assemble part of the product on their own, but they hit a wall when they can't find a specific answer to a complex problem. This is compounded by issues like the manual being lost, difficult to understand, or not having the exact information they need readily available.

This inability to get a quick answer leads to a cycle of frustration. The user can't properly use the product, which makes them feel like their purchase was a waste of time and money. This could lead to them returning the item, hiring a professional for a simple fix, or even abandoning the product altogether. Essentially, the manual, which is meant to be a resource, becomes a barrier to a good customer experience.

## Task 2

### ManualAIze: The Intuitive Digital Assistant
My proposed solution is an AI-powered tool called ManualAIze, which transforms static, confusing product manuals into an interactive and intelligent resource. The user's experience is simple: they either upload a PDF of their manual or let the tool find it online. This instantly creates a personalized, digital manual library that is always accessible and never lost.

In this new world, the user's experience is transformed. They can ask questions in their own words, like "How do I attach the handle to the main body?" and receive clear, step-by-step instructions in their preferred language. The tool doesn't just restate what's in the manual; it provides tailored troubleshooting, checks for product compatibility, and anticipates common user pain points, making the entire setup and maintenance process feel intuitive and frustration-free.

### Stack
- **Generation LLM**: GPT-4.o-mini, for its larger context window in order to account for multiple very large manuals
- **Embedding Model**: We'll leverage OpenAI's text-embedding-3-small because it's a very powerful (and low-cost) embedding model.
- **Orchestration**: gpt-4.o-mini, We want to leverage the larger token size of 4.1. The orchestrators have to understand multiple complex and domain specific prompts plus evaluate the output of multiple nodes across multiple steps and process context from different tools. It also has to decide if the latest answer addresses the query or not
- **Vector Database**: Qdrant for iteration speed. I have limited time to dedicate to the assignment so I will create a basic version of RAG and will optimize it in a second moment
- **Monitoring**: Langsmith because it is easy to setup, provides in depth analysis and it is efficient
- **Evaluation**: RAGAS because it is easy to setup, provides in depth analysis and it is efficient. I am using gpt-4.1-nano as the RAGAS question generator and gpt 4.1 as the evaluator to leverage the large token limit
- **User Interface**: Next.js, react and TypeScript

### Why an agent?
I am using an agent to evaluate if the context retrieved from the grounding docs is enough to answer the user's query. If not then the agent calls tavily to run an internet search and gather more information. Once it is satisfied with the information it gathered it then passes it to the writer llm that creates the response to show the user

## Task 3
- **Data for RAG**: pdf manuals stored in memory
- **Search API**: Tavily
- **Chunking strategy**: standard, chunk size 1000, overlap 200

## Task 4
Done in development_v1.ipynb

## Task 5

| Metric | Score |
|--------|-------|
| Context Recall | 0.7111 |
| Faithfulness | 0.7682 |
| Factual Correctness (F1) | 0.3283 |
| Answer Relevancy | 0.942 |
| Context Entity Recall | 0.2098 |

Based on the RAGAS evaluation, the system demonstrates a to perform well in producing relevant answers, as indicated by the high answer_relevancy score of 0.9690. However, the performance is limited in its retrieval and generation components. The low context_recall (0.3875) and context_entity_recall (0.2386) scores suggest that the system is not doing a good job at retrieving all the necessary information from the source documents to fully answer the queries. This is a primary cause for the low faithfulness (0.6986) and factual_correctness (0.3358) scores, as the generated answers are often unsupported by the retrieved context or contain factual errors. Furthermore, the system's susceptibility to noise is a concern, with a noise_sensitivity score of 0.3825, meaning its performance degrades notably when irrelevant information is present in the context, likely indicating that the prompt or llm ownership structure can be improved. In summary, while the system effectively stays on topic, it struggles to retrieve the right information and to generate factually accurate and well-supported answers based on the provided context.

**Next steps to try to improve the performance are:**
- experiment with different retrieval methods, eg reranking, ensemble
- update the prompts to the llm agents
- experiment with different chunking strategies, eg semantic
- use wider online search
- update the agent's architecture to split each llm into a single focused agent

## Task 6

### Advanced retrieval techniques

**Cohere Reranking**: Given a set of retrieved documents, rank them based on their semantic relevance using an internal llm and return the top K as define by the user.

*Why*: given that the naive retrieval returns a large number of documents (15) there is a high chance that many of these documents are not relevant and end up adding noise to the answer. Reranking and selecting only the top K docs should help focus the retrieved context and limit the noise

**BM25**: is a probabilistic keyword-based retrieval algorithm that ranks documents by estimating their relevance to a search query, primarily by considering the frequency and position of keywords within a document and across the entire dataset.

*Why*: the documents we are processing are instructions manuals and therefore are technical documents. There is a high chance that the user will use keywords to write their query. We want to make sure that we include all the most relevant docs that include those keywords.

**Ensemble**: is a method that combines the search results from multiple distinct retrieval algorithms, such as keyword-based (sparse) and vector-based (dense) search, to create a more comprehensive and robust set of retrieved documents for the generation model.

*Why*: it leverages the strengths of multiple retrieval methods to overcome their individual weaknesses, resulting in a more comprehensive and accurate set of retrieved documents

Tested in development_v1.ipynb

## Task 7

### Raw results table

| Metric | Naive Score | Compression Score | Ensemble Score |
|--------|-------------|------------------|----------------|
| Context Recall | 0.3875 | 0.3458 | 0.675 |
| Faithfulness | 0.6986 | 0.6266 | 0.7071 |
| Factual Correctness (F1) | 0.3358 | 0.3717 | 0.4258 |
| Answer Relevancy | 0.969 | 0.934 | 0.9643 |
| Context Entity Recall | 0.2386 | 0.2339 | 0.2626 |
| Noise Sensitivity (Relevant) | 0.3825 | 0.3194 | 0.4087 |

### Delta table wrt naive retrieval

| Metric | Naive Score | Compression Score | Ensemble Score |
|--------|-------------|------------------|----------------|
| Context Recall | 0 | -0.0417 | 0.2875 |
| Faithfulness | 0 | -0.072 | 0.0085 |
| Factual Correctness (F1) | 0 | 0.0359 | 0.09 |
| Answer Relevancy | 0 | -0.035 | -0.0047 |
| Context Entity Recall | 0 | -0.0047 | 0.024 |
| Noise Sensitivity (Relevant) | 0 | -0.0631 | 0.0262 |

We use Naive retrieval strategy as our control. When we compare the advanced retrieval methods against this baseline we see the following:

**Compression**: This strategy appears to be a poor choice for our application. The negative changes in Faithfulness (-0.072) and Context Recall (-0.0417) are major red flags. This indicates that compressing the documents is causing the model to become less grounded in the source material and is losing critical information. The small gain in Factual Correctness is not enough to justify the substantial decrease in the system's ability to provide well-supported and comprehensive answers. Likely the reranking is causing us to lose too much relevant information.

**Ensemble**: This is the most promising strategy and the clear winner for our use case. It delivers a positive change in the most relevant metrics for a manual-based application:

- **Context Recall**: The most significant gain is a positive change of +0.2875, indicating that the ensemble method is far more effective at retrieving all the necessary context to answer a user's question.
- **Factual Correctness (F1)**: With a positive change of +0.09, this strategy proves that it can generate more factually accurate responses, which is paramount for troubleshooting.
- **Faithfulness**: While the gain is small (+0.0085), it shows an improvement over the baseline, unlike the compression method.

While the Answer Relevancy score saw a negligible drop, the major improvements in core retrieval and generation quality make the Ensemble strategy the superior choice for further development.

## Appendix

### Future work

#### High-Priority Action Items (Core Functionality)

**1. Fix State Management Bug to Ensure Conversational Context**
- **Limitation**: Each step in the agent's workflow overwrites the history from previous steps. This means the Router only sees the retrieved documents (not the original question), and the Writer only sees the web search results (not the retrieved documents or the question). This is a critical bug that prevents the agent from making informed decisions.
- **Proposed Solution**:
  - Modify the retrieve_node and search_agent_node in backend/app/graph/nodes.py.
  - Instead of returning a brand new list of messages, these nodes should append their output to the existing state["messages"] list.
  - This will ensure that context is correctly passed and accumulated throughout the workflow, allowing the Writer and Router to have a complete picture.

**2. Implement Persistent Vector Storage**
- **Limitation**: The vector database is stored in memory, which means all PDF documents are re-processed and re-indexed every time the application starts. This is inefficient and leads to long startup times.
- **Proposed Solution**:
  - Modify the load_documents_and_create_retriever function in backend/app/graph/builder.py.
  - Configure the Qdrant vector store to save its data to a file on disk (e.g., by changing location=":memory:" to a path like path="./qdrant_data").
  - Add logic to check if a database already exists at that path on startup. If it does, load it directly instead of rebuilding it from the PDFs.

#### Medium-Priority Action Items (Reliability and Performance)

**3. Implement Robust Error Handling for Document Loading**
- **Limitation**: The application currently prints an error and continues if a PDF fails to load. This can lead to the agent operating with an incomplete knowledge base without any clear warning.
- **Proposed Solution**:
  - Introduce Structured Logging: Replace all print() statements used for status or error reporting with Python's standard logging module. This will provide more context (timestamps, severity levels) and control over the output.
  - Create a Configurable Failure Policy: Implement an environment variable (e.g., DOC_LOAD_FAILURE_POLICY) that allows choosing between:
    - FAIL_FAST (Default): The application will stop immediately if any document fails to load.
    - CONTINUE_WITH_WARNING: The application will log the error but continue running with the successfully loaded documents.

**4. Optimize the Routing Mechanism**
- **Limitation**: The current router_node uses a powerful LLM (gpt-4o-mini) to make a simple decision: whether to search the web or write an answer. This adds unnecessary cost and latency to each request.
- **Proposed Solution (for discussion)**:
  - Explore replacing the LLM-based router with a deterministic approach. For example, we could inspect the confidence scores provided by the Cohere reranker in the retrieve_node. If the scores are above a certain threshold, we route to the Writer; if not, we route to Search. This would be significantly faster and cheaper.
  - Alternatively, use a much smaller and faster model specifically for the routing task.

#### Low-Priority Action Items (Good Practices and Future-Proofing)

**5. Centralize Configuration**
- **Limitation**: Key settings like model names (gpt-4o-mini), file paths (./data), and collection names (Manuals) are hardcoded directly in the source code. This makes the application inflexible and harder to manage.
- **Proposed Solution**:
  - Refactor the code in builder.py and nodes.py to pull these values from environment variables or a dedicated configuration file (config.py).

**6. Allow for Dynamic Document Management**
- **Limitation**: The agent can only work with the PDF files present in the /data folder at startup. There is no way to add, remove, or update documents while the application is running.
- **Proposed Solution (Future Enhancement)**:
  - Design and implement new API endpoints in main.py for document management. This could include endpoints for:
    - Uploading new PDF files.
    - Deleting existing files.
    - Triggering a re-indexing of the document collection.

### MVP flow

The initial flow should be for a user that has a new car seat and wants to know if it can be installed in the middle seat of their car or their partner's car.

The flow starts with the user selecting a button "+ new project" and giving it a name. Then the user can either upload the manuals themselves. The agent will process the given data, store them in memory for now. Once the data is processed the user will be able to select the tab project name and the UI will present a chat interface where the user can ask questions to the agent

### Nice to have
- The user can also prompt the agent to look online for links to guides or videos
- generate the text version of the assembly instructions
- the agent fills the registration form to send the company
- add search and download functionality for when the user wants the agent to download the manual 