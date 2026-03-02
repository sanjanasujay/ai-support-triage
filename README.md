# AI Support Ticket Triage Backend

A FastAPI-based backend service that automates support ticket classification and routing using LLM-powered structured outputs.

## Features

- REST API for ticket submission and retrieval
- LLM-based category and urgency classification
- Confidence scoring with automatic escalation
- PostgreSQL persistence
- Basic metrics endpoint
- Dockerized deployment
- Pytest-based API tests

## Tech Stack

Python, FastAPI, PostgreSQL, SQLAlchemy (async), OpenAI API (Structured Outputs), Docker, Pytest

## Quickstart (Docker)

1. Copy environment template:

```bash
cp .env.example .env
```

2. Add your OpenAI key to `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/triage
CONFIDENCE_THRESHOLD=0.75
```

3. Build and start the application:

```bash
docker compose up --build
```

4. Open Swagger UI in your browser:

http://localhost:8000/docs

## API Endpoints

- POST /tickets
- GET /tickets/{id}
- GET /metrics/basic
- GET /health

## Example Request

```bash
curl -X POST "http://localhost:8000/tickets" \
  -H "Content-Type: application/json" \
  -d @samples/ticket_access_403.json
```

## Running Tests

```bash
docker compose exec api pytest -q
```
