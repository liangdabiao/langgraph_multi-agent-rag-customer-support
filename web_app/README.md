# Web Application for Multi-Agent RAG Customer Support

This directory contains the FastAPI web application that provides a multi-user chat interface for the customer support system.

## Installation

1. Navigate to this directory: `cd web_app`
2. Install dependencies: `poetry install`

## Running the Application

1. Ensure the main project dependencies are installed and the Qdrant service is running.
2. From this directory, run: `poetry run uvicorn web_app.app.main:app --reload --host 0.0.0.0 --port 8000`
3. Access the application in your browser at `http://localhost:8000`