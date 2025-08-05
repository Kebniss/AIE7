FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files (handle missing poetry.lock gracefully)
COPY pyproject.toml ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (this will generate poetry.lock if it doesn't exist)
RUN poetry install --no-interaction --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "python", "-m", "backend.app.main"] 