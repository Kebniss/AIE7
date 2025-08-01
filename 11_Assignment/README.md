# ManualAIze

AI-powered application for manual processing and automation.

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
