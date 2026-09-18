# AI PR Review Agent

An AI Pull Request Review Agent built in Python using FastAPI.

## Current Progress

- **Project Initialization**: Set up the basic project structure and virtual environment.
- **Dependencies**: Added `fastapi` and `uvicorn` to `requirements.txt`.
- **API Endpoints**: Created the foundational FastAPI application (`app/main.py`) with:
  - `GET /`: Root endpoint returning a welcome message `{"message": "AI PR Review Agent is running!"}`.
  - `GET /health`: Health-check endpoint returning `{"status": "healthy"}` for uptime monitoring.

## How to Run Locally

1. **Activate the Virtual Environment**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(For bash/zsh use `source .venv/bin/activate`)*

2. **Start the FastAPI server**:
   ```powershell
   uvicorn app.main:app --reload
   ```

3. **Access the API**:
   - Application: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - Interactive API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
