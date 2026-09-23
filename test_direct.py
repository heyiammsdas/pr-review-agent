import asyncio
import json
from app.graph.review_graph import review_graph

async def main():
    initial_state = {
        "repository": "heyiammsdas/testing-pr-agent",
        "pr_number": 1,
        "pr_details": {},
        "pr_diff": "",
        "security_review": {},
        "quality_review": {},
        "testing_review": {},
        "final_review": {}
    }
    final_state = await review_graph.ainvoke(initial_state)
    print(json.dumps(final_state["final_review"], indent=2))

asyncio.run(main())
