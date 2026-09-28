# AI PR Review Agent

## Overview

The AI PR Review Agent is an automated code review assistant that listens for GitHub Pull Request events via webhooks, analyzes the changed files using an intelligent multi-agent LangGraph workflow, and posts a structured review directly as a GitHub comment.

It features a Retrieval-Augmented Generation (RAG) system utilizing FAISS to retrieve relevant repository context, ensuring that the agents (Security, Quality, and Testing) understand the broader codebase before leaving file- and line-specific feedback.

## Architecture

```text
Developer
   ↓
GitHub Pull Request
   ↓
GitHub Webhook
   ↓
FastAPI
   ↓
Redis Queue
   ↓
Background Worker
   ↓
LangGraph
   ↓
RAG / FAISS (Repository Context)
   ↓
┌────────────┬────────────┬────────────┐
│ Security   │ Quality    │ Testing    │
│ Agent      │ Agent      │ Agent      │
└────────────┴────────────┴────────────┘
             ↓
         Aggregator
             ↓
       Final AI Review
             ↓
      GitHub PR Comment
```

## Key Features

- **Webhook Integration**: Listens to GitHub PR `opened`, `synchronize`, and `reopened` events.
- **Asynchronous Processing**: Uses Redis for queueing review jobs, allowing the API to respond immediately.
- **Multi-Agent Architecture**: Separate AI agents focus on Security, Code Quality, and Testing.
- **Context-Aware (RAG)**: Embeds the entire repository using FAISS to provide agents with relevant project context.
- **File and Line Level Findings**: Precisely maps findings to the exact file and line number in the unified git diff.
- **Automated Comments**: Posts nicely formatted Markdown comments back to the GitHub PR.
- **Dockerized**: Fully containerized setup for API, Worker, and Redis.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Web server & Webhook endpoint |
| Redis | Job queue and state management |
| LangGraph | Orchestration of the multi-agent workflow |
| Google Gemini API | Large Language Model backing the review agents |
| FAISS & NumPy | Vector database for RAG context retrieval |
| Docker & Compose | Containerization and local orchestration |
| Pytest | Mock, unit, and integration testing |

## How It Works

1. A developer creates or updates a Pull Request on GitHub.
2. GitHub sends a webhook payload to the FastAPI `/webhook/github` endpoint.
3. The API verifies the signature, creates a unique `job_id`, queues it in Redis, and returns `200 OK`.
4. A background Worker pops the job from Redis and triggers the LangGraph workflow.
5. The system fetches the PR details and the raw diff from GitHub.
6. The RAG pipeline performs a similarity search over the repository files using FAISS to find context.
7. The Security, Quality, and Testing agents run in parallel, analyzing the code changes (and context) to find issues.
8. The Aggregator agent compiles the findings, validates line numbers against the Git diff, and produces a final summary.
9. A structured Markdown comment is posted back to the PR on GitHub.
10. The job status is marked as `completed` in Redis.

## Project Structure

```text
pr-review-agent/
├── app/
│   ├── agents/          # Security, Quality, Testing, and Aggregator agents
│   ├── graph/           # LangGraph workflow definition
│   ├── rag/             # Loader, Chunker, Embedder, and FAISS Indexer
│   ├── services/        # GitHub API, LLM, Job Queue, Diff Parser, Formatter
│   ├── main.py          # FastAPI application
│   └── worker.py        # Background job processor
├── tests/               # Unit, integration, and mock tests
├── .env.example         # Template for environment variables
├── .dockerignore        # Docker build exclusions
├── .gitignore           # Git tracking exclusions
├── docker-compose.yml   # Multi-container setup
├── Dockerfile           # Unified image for API and Worker
└── requirements.txt     # Python dependencies
```

## Prerequisites

- Python 3.12 or 3.13
- Docker and Docker Compose (optional, for containerized setup)
- Git
- GitHub account and a Personal Access Token (PAT)
- Google Gemini API Key

## Environment Variables

Create a `.env` file in the root directory (do not commit this file):

```properties
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
REDIS_URL=redis://localhost:6379/0
```

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd pr-review-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment:**
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment:**
   Copy `.env.example` to `.env` and fill in your actual API keys.

6. **Start Redis** (If running locally without Docker).

7. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

8. **Start the Worker:**
   ```bash
   python -m app.worker
   ```

## Docker Setup

To run the entire stack (API, Worker, and Redis) using Docker Compose:

1. **Build and start the containers:**
   ```bash
   docker compose up --build -d
   ```

2. **View logs:**
   ```bash
   docker compose logs -f
   ```

3. **Stop the containers:**
   ```bash
   docker compose down
   ```

## API Endpoints

### `GET /health`
- **Purpose**: Verifies that the FastAPI server is running.
- **Response**: `{"status": "ok"}`

### `POST /review`
- **Purpose**: Manually trigger a PR review job.
- **Request**:
  ```json
  {
    "repository": "owner/repo",
    "pr_number": 42
  }
  ```
- **Response**:
  ```json
  {
    "job_id": "uuid-string",
    "status": "queued"
  }
  ```

### `GET /review/{job_id}`
- **Purpose**: Check the status of a queued or completed review job.
- **Response**:
  ```json
  {
    "job_id": "uuid-string",
    "status": "completed",
    "result": { ... }
  }
  ```

### `POST /webhook/github`
- **Purpose**: Endpoint for GitHub to send PR events.
- **Headers**: Must include valid `X-Hub-Signature-256`.
- **Response**: `{"message": "Webhook received", "job_id": "uuid-string", "status": "queued"}`

## GitHub Webhook Setup

1. Go to your GitHub repository -> **Settings** -> **Webhooks** -> **Add webhook**.
2. **Payload URL**: `https://<your-domain>/webhook/github`
3. **Content type**: `application/json`
4. **Secret**: Enter the exact string from your `GITHUB_WEBHOOK_SECRET` environment variable.
5. **Which events**: Select **Let me select individual events**, and check **Pull requests**.
6. Ensure the webhook is marked **Active**.

## RAG Pipeline

The Retrieval-Augmented Generation (RAG) system enables the agents to understand the repository context:
1. **File Loading**: Downloads and reads the codebase structure.
2. **Chunking**: Splits the codebase into manageable segments.
3. **Embeddings**: Uses the Gemini API to create vector embeddings for the chunks.
4. **FAISS**: Indexes the embeddings for fast vector similarity search.
5. **Similarity Search**: When a PR is reviewed, the diff is used as a query to find the most relevant contextual files.

## LangGraph Workflow

The workflow relies on a state graph:
- **State**: Holds `pr_details`, `pr_diff`, and the individual reviews.
- **Nodes**:
  - `run_security_review`
  - `run_quality_review`
  - `run_testing_review`
  - `run_aggregator_agent`

The security, quality, and testing nodes execute in parallel. Their outputs are then passed to the aggregator node, which normalizes the findings and validates the line numbers against the parsed diff.

## AI Review Agents

- **Security Agent**: Scans for vulnerabilities, hardcoded secrets, and unsafe practices.
- **Quality Agent**: Reviews for code readability, maintainability, and anti-patterns.
- **Testing Agent**: Identifies missing tests and edge cases.
- **Aggregator**: Consolidates the outputs, removes duplicates, and ensures all file/line mappings strictly adhere to the git diff.

## Review Output Example

```markdown
## 🤖 AI PR Review

### Summary

This PR introduces authentication logic but contains a critical security flaw.

### 🔴 Security

**`src/auth.py:42`**

**Hardcoded secret**

A secret appears to be hardcoded in the changed code.

**Suggestion:** Move the secret to an environment variable.

### 🟡 Code Quality

**`src/auth.py:15`**

**Complex Function**

This function has too many nested loops.

**Suggestion:** Refactor into smaller helper functions.

### Testing

No testing issues found.

### Review Statistics

| Category | Count |
|---|---:|
| Security | 1 |
| Code Quality | 1 |
| Testing | 0 |
| Total | 2 |
```

## Testing

Run tests using pytest:

```bash
python -m pytest tests
```

- **Unit / Mock Tests**: Extensive tests exist for diff parsing, finding validation, and the graph pipeline using `unittest.mock`. External API calls (Gemini/GitHub) are thoroughly mocked out so tests run locally without credentials or quota limitations.

## Security

- `.env` files are ignored by git and never committed.
- API keys are exclusively accessed via environment variables.
- GitHub webhooks require a strict SHA-256 signature verification.
- Internal error traces are masked from the final PR comments to avoid leaking infrastructure details.

## Development Status

- [x] FastAPI skeleton
- [x] GitHub API integration
- [x] Redis Job Queue & Worker
- [x] Webhook Signature Verification
- [x] LangGraph Multi-Agent Orchestration
- [x] Gemini API Integration
- [x] RAG / FAISS Implementation
- [x] File and Line-level Mapping
- [x] Automated PR Comments
- [x] Dockerization

## Roadmap

- Implement advanced caching for the FAISS index across multiple PRs for the same repo.
- Support for inline comments directly on GitHub PR lines via the GitHub Review API.

## License

License not yet specified.

## Reviewer Guide

To quickly run this project to evaluate it:
1. Clone the repo and provide an `.env` with a `GITHUB_TOKEN` and `GEMINI_API_KEY`.
2. Run `docker compose up --build -d`.
3. Test locally using:
   `curl -X POST http://localhost:8000/review -H "Content-Type: application/json" -d "{\"repository\": \"owner/repo\", \"pr_number\": 1}"`
4. Use `docker compose logs -f worker` to watch the AI agents process the review!
