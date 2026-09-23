import time
import asyncio
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

from app.services.github import get_pr_details, get_pr_diff
from app.agents.security_agent import run_security_review
from app.agents.quality_agent import run_quality_review
from app.agents.testing_agent import run_testing_review
from app.agents.aggregator_agent import run_aggregator_agent

class ReviewState(TypedDict):
    repository: str
    pr_number: int
    pr_details: dict
    pr_diff: str
    security_review: dict
    quality_review: dict
    testing_review: dict
    final_review: dict

async def get_pr_context(state: ReviewState) -> dict:
    print("[Graph Node] get_pr_context started")
    repo = state["repository"]
    pr_num = state["pr_number"]
    
    # Run synchronous GitHub API calls in threads
    pr_details = await asyncio.to_thread(get_pr_details, repo, pr_num)
    pr_diff = await asyncio.to_thread(get_pr_diff, repo, pr_num)
    
    print("[Graph Node] get_pr_context completed")
    return {"pr_details": pr_details, "pr_diff": pr_diff}

async def security_agent_node(state: ReviewState) -> dict:
    print("[Graph Node] security_agent started")
    try:
        review = await asyncio.to_thread(run_security_review, state["pr_diff"])
    except Exception as e:
        print(f"[Graph Node] security_agent failed: {e}")
        review = {"issues": []}
    print("[Graph Node] security_agent completed")
    return {"security_review": review}

async def quality_agent_node(state: ReviewState) -> dict:
    print("[Graph Node] quality_agent started")
    try:
        review = await asyncio.to_thread(run_quality_review, state["pr_diff"])
    except Exception as e:
        print(f"[Graph Node] quality_agent failed: {e}")
        review = {"issues": []}
    print("[Graph Node] quality_agent completed")
    return {"quality_review": review}

async def testing_agent_node(state: ReviewState) -> dict:
    print("[Graph Node] testing_agent started")
    try:
        review = await asyncio.to_thread(run_testing_review, state["pr_diff"])
    except Exception as e:
        print(f"[Graph Node] testing_agent failed: {e}")
        review = {"issues": []}
    print("[Graph Node] testing_agent completed")
    return {"testing_review": review}

async def aggregator_node(state: ReviewState) -> dict:
    print("[Graph Node] aggregator started")
    try:
        final_review = await asyncio.to_thread(
            run_aggregator_agent,
            state["security_review"],
            state["quality_review"],
            state["testing_review"]
        )
    except Exception as e:
        print(f"[Graph Node] aggregator failed: {e}")
        final_review = {
            "summary": "Aggregation failed due to API error.", 
            "issues": [], 
            "statistics": {"total": 0, "security": 0, "code_quality": 0, "testing": 0}
        }
    print("[Graph Node] aggregator completed")
    return {"final_review": final_review}

def build_review_graph():
    # 1. Initialize Graph with ReviewState
    builder = StateGraph(ReviewState)
    
    # 2. Add Nodes
    builder.add_node("get_pr_context", get_pr_context)
    builder.add_node("security_agent", security_agent_node)
    builder.add_node("quality_agent", quality_agent_node)
    builder.add_node("testing_agent", testing_agent_node)
    builder.add_node("aggregator", aggregator_node)
    
    # 3. Add Edges
    # START -> get_pr_context
    builder.add_edge(START, "get_pr_context")
    
    # get_pr_context branches to the three parallel agents
    builder.add_edge("get_pr_context", "security_agent")
    builder.add_edge("get_pr_context", "quality_agent")
    builder.add_edge("get_pr_context", "testing_agent")
    
    # The three agents all flow into the aggregator node
    builder.add_edge(["security_agent", "quality_agent", "testing_agent"], "aggregator")
    
    # aggregator -> END
    builder.add_edge("aggregator", END)
    
    # 4. Compile Graph
    return builder.compile()

# Instantiate the compiled graph so we can use it globally
review_graph = build_review_graph()
