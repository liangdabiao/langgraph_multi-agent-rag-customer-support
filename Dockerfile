# Base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry files
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY customer_support_chat /app/customer_support_chat
COPY vectorizer /app/vectorizer

# Set environment variables
ENV PYTHONPATH="/app"

# Expose port if running a server (adjust as needed)
EXPOSE 8501

# Default command
CMD ["python", "-m", "customer_support_chat.app.main"]