# ManualAIze

AI-powered application for manual processing and automation.

## 📋 TLDR: Development Progress (development_v1.ipynb)

### 🎯 What Was Accomplished

**ManualAIze** is an AI agent system designed to parse and retrieve information from user manuals. The development notebook (`development_v1.ipynb`) successfully implemented:

#### 🔧 **Core Agent Architecture**
- **Multi-agent system** with specialized roles: Retrieval, Router, Search, and Writer
- **LangGraph-based workflow** with conditional routing between agents
- **PDF processing pipeline** using PyPDFLoader for fast document loading
- **Vector storage** with Qdrant for semantic search capabilities

#### 📊 **Retrieval Strategy Evaluation**
Tested and compared three retrieval approaches:
1. **Naive Retrieval** - Basic vector similarity search
2. **Compression Retrieval** - Enhanced with Cohere reranking
3. **Ensemble Retrieval** - Combined BM25 + compression strategies

#### 🧪 **Performance Evaluation with RAGAS**
- **Generated test dataset** from 100 PDF documents using RAGAS TestsetGenerator
- **Evaluated 6 key metrics**: Context Recall, Faithfulness, Factual Correctness, Response Relevancy, Context Entity Recall, Noise Sensitivity
- **Results comparison** across all three retrieval strategies

#### 📝 **Key Findings**
- **Ensemble retrieval** showed best factual correctness (+7.25% vs naive)
- **Context entity recall** improved with ensemble approach (+5.26% vs naive)
- **Faithfulness** maintained high scores across all strategies
- **Answer relevancy** remained consistently high (>87% across all methods)

#### 🛠️ **Technical Stack**
- **LangChain** for agent orchestration
- **OpenAI GPT-4** for LLM capabilities
- **Cohere** for document reranking
- **Qdrant** for vector storage
- **RAGAS** for evaluation framework

## 🌐 Web Application Implementation

### 🏗️ **Architecture Overview**

The web application is built as a **full-stack system** with:
- **Frontend**: Next.js 15 with React 19 and TypeScript
- **Backend**: FastAPI with LangGraph agent orchestration
- **Database**: Qdrant vector database for document storage
- **Containerization**: Docker Compose for easy deployment

### 🔧 **Backend Implementation (`/backend`)**

#### **FastAPI Server** (`app/main.py`)
- **Streaming responses** using Server-Sent Events (SSE)
- **CORS middleware** configured for frontend communication
- **Graph lifecycle management** with startup/shutdown handlers
- **Error handling** with detailed HTTP status codes

#### **Agent Graph Architecture** (`app/graph/`)
- **State management** with `AgentState` for message flow
- **Modular node system**:
  - `retrieve_node`: Document retrieval with compression
  - `router_node`: LLM-based routing between agents
  - `search_node`: Internet search capabilities
  - `writer_node`: Final answer generation
- **Tool integration** with Tavily search API

#### **Document Processing Pipeline**
- **PDF loading** with PyPDFLoader for performance
- **Text chunking** with RecursiveCharacterTextSplitter
- **Vector embedding** using OpenAI text-embedding-3-small
- **Persistent storage** in Qdrant with collection management

### 🎨 **Frontend Implementation (`/frontend`)**

#### **Next.js Application** (`src/app/`)
- **Modern React 19** with TypeScript for type safety
- **Real-time chat interface** with streaming responses
- **Markdown rendering** with mathematical notation support (KaTeX)
- **Responsive design** with CSS modules

#### **Key Features**
- **Streaming chat** with Server-Sent Events integration
- **Error handling** with detailed user feedback
- **Mathematical notation** rendering with LaTeX support
- **Auto-scrolling** chat interface
- **Loading states** and progress indicators

#### **UI Components**
- **Sidebar** with system information and controls
- **Chat container** with message history
- **Input form** with textarea and send button
- **Error display** with actionable instructions

### 🐳 **Deployment & Infrastructure**

#### **Docker Configuration**
- **Multi-service setup** with docker-compose.yml
- **Qdrant database** container for vector storage
- **Backend service** with Python 3.11 and Poetry
- **Frontend service** with Node.js 18 and Next.js

#### **Service Communication**
- **Backend API** exposed on port 8000
- **Frontend dev server** on port 3002
- **Qdrant database** on ports 6333/6334
- **Internal networking** with Docker bridge

### 🔄 **Data Flow**

1. **User Input** → Frontend chat interface
2. **API Request** → Backend `/invoke` endpoint
3. **Agent Processing** → LangGraph workflow execution
4. **Streaming Response** → Real-time SSE updates
5. **UI Update** → Markdown rendering with math support

### 🚀 **Quick Start**

```bash
# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3002
# Backend API: http://localhost:8000
# Qdrant: http://localhost:6333
```

### 🛠️ **Development Setup**

```bash
# Backend development
cd backend
poetry install
poetry run python -m backend.app.main

# Frontend development
cd frontend
npm install
npm run dev
```

### 🚀 Next Steps
The agent system is ready for integration with the web interface and can handle real-time queries about car manuals, car seats, and other technical documents.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd 11_Assignment
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**:
   ```bash
   uv shell
   ```

### Development Setup

1. **Install development dependencies**:
   ```bash
   uv sync --extra dev
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Format code**:
   ```bash
   black .
   isort .
   ```

4. **Lint code**:
   ```bash
   flake8 .
   mypy .
   ```

## 📁 Project Structure

```
11_Assignment/
├── manualaize/          # Main package
│   └── __init__.py
├── data/                # Data files
├── development.ipynb    # Development notebook
├── main.py             # Entry point
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## 🛠️ Available Tools

### Core Dependencies
- **OpenAI**: AI/LLM integration
- **Jupyter**: Interactive development
- **Pandas & NumPy**: Data manipulation
- **Matplotlib & Seaborn**: Data visualization
- **Scikit-learn**: Machine learning
- **FastAPI**: Web API framework
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

## 🔧 Configuration

The project uses `pyproject.toml` for configuration:

- **Python version**: 3.13+
- **Code formatting**: Black with 88 character line length
- **Import sorting**: isort with Black profile
- **Type checking**: mypy with strict settings

## 🚀 Usage

### Running the Application

```bash
# Activate the environment
uv shell

# Run the main application
python main.py

# Or run with specific modules
python -m manualaize
```

### Jupyter Development

```bash
# Start Jupyter notebook
jupyter notebook

# Or start Jupyter lab
jupyter lab
```

### API Development

```bash
# Run FastAPI server
uvicorn main:app --reload
```

## 📝 Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For support and questions, please [create an issue](link-to-issues).
