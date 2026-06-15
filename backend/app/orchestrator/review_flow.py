"""
Review Flow Orchestrator powered by LangGraph.

The function signature and return format remain stable so the frontend
can submit reviews without knowing about the internal graph.
"""

from app.graph.review_graph import run_review_pipeline


def run_review_flow(input_data: dict) -> dict:
    """
    Run the full review verification pipeline.
    
    This entry point runs LangGraph + LangChain + Groq.
    
    Args:
        input_data: dict with business_id, bill_id, review_text, has_media
    
    Returns:
        dict with final_trust_score, trust_level, breakdown, recommendation, action
        (same format the frontend expects)
    """
    return run_review_pipeline(input_data)
