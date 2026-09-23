# AI PR Review Agent

A Python-based AI Pull Request review system that analyzes GitHub Pull Requests using specialized AI review agents. The system uses FastAPI, Gemini, and LangGraph to organize the review workflow.

## 1. Overview

The system takes a GitHub Pull Request, retrieves its details and code diff, and uses multiple specialized review agents to analyze different aspects of the changes.

The current specialized agents are:
- **Security Agent**
- **Code Quality Agent**
- **Testing Agent**

Their results are passed to an Aggregator Agent that produces a structured final review.

## 2. Current Architecture

```text
GitHub Pull Request
        ↓
     FastAPI
        ↓
   GitHub API
        ↓
     PR Diff
        ↓
   LangGraph Workflow
        ↓
 ┌──────┼──────┐
 ↓      ↓      ↓
Security Quality Testing
 Agent    Agent   Agent
 └──────┼──────┘
        ↓
   Aggregator
        ↓
  Final Review
```

## 3. Features

- GitHub Pull Request retrieval
- Pull Request diff retrieval
- FastAPI backend
- Gemini API integration
- Security review agent
- Code quality review agent
- Testing review agent
- Aggregator agent
- Structured review output
- LangGraph-based orchestration
- Redis-based background job queue
- Mock tests for LangGraph workflow
- Environment-based API key configuration

## 4. Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Main programming language |
| FastAPI | Backend API |
| Redis | Job queue and background state storage |
| GitHub REST API | Pull Request data and diff |
| Gemini API | AI analysis |
| LangGraph | Agent workflow orchestration |
| Pydantic | Structured data validation |
| HTTPX | HTTP requests |
| python-dotenv | Environment variables |

## 5. LangGraph Workflow

LangGraph is used to organize the review process as a workflow.

Each specialized agent is represented as a node, and a shared state carries the Pull Request information and review results between nodes.

- **State**: A shared dictionary structure that holds the PR details, the code diff, and the outputs from each specialized agent.
- **Nodes**: Individual Python functions that execute a step in the workflow (e.g., retrieving the PR context or running a specific AI agent).
- **Edges**: The paths that connect the nodes. Our workflow branches in parallel to the specialized agents, and then converges them.
- **Aggregator**: The final node that waits for all parallel agents to finish, reads their findings from the state, and combines them into a single, deduplicated structured review.

## 6. Project Structure

```text
pr-review-agent/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── worker.py
├── tests/
│   ├── test_redis_pipeline.py
│   └── test_review_graph.py
└── app/
    ├── main.py
    ├── agents/
    │   ├── __init__.py
    │   ├── aggregator_agent.py
    │   ├── quality_agent.py
    │   ├── security_agent.py
    │   └── testing_agent.py
    ├── graph/
    │   └── review_graph.py
    └── services/
        ├── __init__.py
        ├── github.py
        ├── job_queue.py
        ├── llm.py
        ├── redis_client.py
        └── review.py
```

## 7. Setup

Run the following commands in PowerShell (Windows-friendly setup):

```powershell
git clone <repository-url>
cd pr-review-agent

python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt
```

**Environment Variables:**
Create your `.env` file from the example template:
```powershell
copy .env.example .env
```

Open `.env` and configure your API keys:
```env
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Real API keys must never be committed to source control!)*

## 8. Running the Application

To start the FastAPI backend server:
```powershell
uvicorn app.main:app --port 8000
```

To process background jobs, start the worker in a separate terminal:
```powershell
python worker.py
```

## 9. API Usage

### `POST /review`
Submits a Pull Request for review.

**Example Request:**
```json
{
  "repository": "owner/repository",
  "pr_number": 1
}
```

**Internal Process:**
1. The API validates the payload and generates a unique job ID.
2. It stores the initial job state (`queued`) in Redis and pushes the ID to the processing queue.
3. The API immediately returns the `job_id` without waiting for the LLMs.
4. The background `worker.py` pops the job from Redis, retrieves the PR data, executes the parallel LangGraph review agents, and updates the final result in Redis.

## 10. Testing

The mock tests verify the LangGraph architecture and the Redis worker pipeline. The mock tests do not call Gemini or external services (like GitHub), allowing you to safely verify the workflow routing.

Run the tests using your active virtual environment:
```powershell
python -m unittest tests.test_review_graph
python -m unittest tests.test_redis_pipeline
```

## 11. Environment Variables

- `GITHUB_TOKEN`: A GitHub Personal Access Token used to retrieve the PR diffs.
- `GEMINI_API_KEY`: Your Google Gemini API key used by the agents for analysis.

## 12. Current Development Status

**Completed:**
- [x] FastAPI backend
- [x] GitHub API integration
- [x] PR diff retrieval
- [x] Gemini integration
- [x] Security Agent
- [x] Quality Agent
- [x] Testing Agent
- [x] Aggregator Agent
- [x] LangGraph workflow
- [x] LangGraph mock testing
- [x] Redis job queue
- [x] Background worker

**In progress:**
- [ ] GitHub Webhooks
- [ ] Repository RAG
- [ ] Vector search
- [ ] Automatic GitHub PR comments
- [ ] Docker/deployment

## 13. Roadmap

- **Phase 1** — Core PR Review
- **Phase 2** — Multi-Agent Review
- **Phase 3** — LangGraph
- **Phase 4** — Redis Background Jobs
- **Phase 5** — GitHub Webhooks
- **Phase 6** — Repository RAG
- **Phase 7** — Automatic PR Comments
- **Phase 8** — Docker & Deployment

## 14. Learning Goals

This project is being built to learn:
- LLM application development
- AI agents
- multi-agent systems
- LangGraph
- GitHub API
- asynchronous/background processing
- Redis
- RAG
- vector search
- webhook-driven systems
- AI application architecture

## 15. How I Explain This Project

This project is an AI-powered Pull Request reviewer built with Python and FastAPI. It uses LangGraph to orchestrate a multi-agent workflow where specialized LLMs analyze code for security vulnerabilities, quality issues, and missing tests in parallel. The system utilizes Redis for a background job queue, decoupling the heavy AI processing from the web API. Ultimately, an aggregator agent synthesizes the findings into a single, cohesive code review.

## 16. Security

- `.env` contains secrets and must not be committed.
- `.env.example` contains placeholders.
- API keys should never be exposed in logs or source code.
