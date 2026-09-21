# AI PR Review Agent

A Python-based AI system that analyzes GitHub Pull Requests and provides structured code-review findings using specialized AI agents powered by the Gemini API.

## Features

- **GitHub REST API Integration**: Dynamically fetches Pull Request metadata and the exact code diffs directly from GitHub.
- **Specialized Multi-Agent Review System**:
  - **Security Agent**: Scans for SQL injection, XSS, hardcoded secrets, and other security vulnerabilities.
  - **Quality Agent**: Analyzes code readability, maintainability, design, and duplicated code.
  - **Testing Agent**: Identifies missing tests, edge cases, and potential regression risks.
- **Structured Outputs**: Forces the AI to return perfectly-structured JSON responses using Pydantic models.
- **FastAPI Backend**: Provides a simple, robust REST endpoint (`/review`) with built-in interactive Swagger documentation.
- **Resilient AI Handling**: Implements exponential backoff retry logic to handle temporary Gemini API throttling and 503 errors safely.
- **Secure Configuration**: Uses `python-dotenv` to ensure all API tokens and secrets remain safely off the codebase.

## Architecture

```ascii
   GitHub PR
       ↓
    FastAPI
       ↓
   GitHub API
       ↓
PR Metadata + Diff
       ↓
┌──────────────┬──────────────┬──────────────┐
│ Security     │ Code Quality │ Testing      │
│ Agent        │ Agent        │ Agent        │
└──────────────┴──────────────┴──────────────┘
       ↓
Structured Review (JSON)
```

## Tech Stack

- **Python** 
- **FastAPI** (Web Framework)
- **Pydantic** (Data Validation & Structured Outputs)
- **GitHub REST API** (Diff extraction)
- **Gemini API** (Google GenAI SDK)
- **HTTPX** (Asynchronous HTTP requests)
- **python-dotenv** (Environment variable management)

## Project Structure

```text
pr-review-agent/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── security_agent.py
│   │   ├── quality_agent.py
│   │   └── testing_agent.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github.py
│   │   └── llm.py
│   └── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd pr-review-agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment (Windows)**:
   ```bash
   .\.venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your keys to `.env`:
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token (PAT)
   - `GEMINI_API_KEY`: Your Google AI Studio Gemini API Key

6. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

Once the server is running, you can access the interactive API documentation at:
**http://localhost:8000/docs**

To trigger a review, send a `POST` request to the `/review` endpoint with a JSON payload:

```json
{
  "repository": "owner/repository",
  "pr_number": 1
}
```

### Example Structured Response
*Note: Exact findings will depend heavily on the content of the Pull Request being analyzed.*

```json
{
  "message": "Review request received",
  "repository": "heyiammsdas/testing-pr-agent",
  "pr_number": 1,
  "pr_details": {
    "title": "Add print statement for 'world'",
    "number": 1,
    "state": "open",
    "html_url": "https://github.com/heyiammsdas/testing-pr-agent/pull/1"
  },
  "pr_diff": "diff --git a/test.py b/test.py\nindex 42fe7d8..b6552fa 100644\n--- a/test.py\n+++ b/test.py\n@@ -1 +1,2 @@\n print(\"hello\") \n+print(\"world\") \n",
  "security_review": {
    "issues": []
  },
  "quality_review": {
    "issues": []
  },
  "testing_review": {
    "issues": []
  }
}
```

## Security

- **Never commit `.env`**: This file contains your highly-sensitive API keys. Ensure it remains in your `.gitignore`.
- **Never expose GitHub or Gemini API keys**: Our application safely masks raw stack traces and handles API key errors internally to prevent accidental exposure to frontend clients.
- `.env.example` contains placeholders only and is completely safe to commit.

## Current Limitations

This project is actively under development. Currently, it **does NOT yet include**:
- GitHub webhooks for automatic PR triggering
- Parallel agent execution (Agents currently run sequentially)
- An Aggregator Agent to summarize findings
- RAG (Retrieval-Augmented Generation) or codebase embeddings
- `pgvector` database storage
- LangGraph orchestration
- Redis or background job queues
- Persistent review databases
- An observability dashboard
- Automatic posting of review comments directly to GitHub PRs

## Roadmap

- [x] Phase 1: Basic PR review
- [x] Phase 2: Specialized agents
- [ ] Phase 3: Aggregator agent
- [ ] Phase 4: GitHub webhook automation
- [ ] Phase 5: RAG + code embeddings
- [ ] Phase 6: pgvector
- [ ] Phase 7: LangGraph orchestration
- [ ] Phase 8: Redis/background jobs
- [ ] Phase 9: Observability
- [ ] Phase 10: Automatic GitHub PR comments
- [ ] Phase 11: Docker + CI/CD
- [ ] Phase 12: Deployment

## Learning Goals

This project serves as a comprehensive educational playground for exploring modern AI engineering concepts, including:
- LLM application development
- AI agents & multi-agent systems
- GitHub API integration
- Forcing structured LLM outputs
- RAG & Vector search
- Workflow orchestration
- Asynchronous AI workflows
- AI observability

## Development Progress

- [x] Step 1-3: Project initialization and API foundation
- [x] Step 4: Add `/health` endpoint
- [x] Step 5: Implement `/review` placeholder 
- [x] Step 6-7: Integrate GitHub API for metadata and diffs
- [x] Step 8: Initial raw Gemini LLM integration
- [x] Step 9: Enforce Structured Outputs via Pydantic
- [x] Step 10: Create Security Agent
- [x] Step 11: Create Code Quality Agent
- [x] Step 12: Create Testing Agent
