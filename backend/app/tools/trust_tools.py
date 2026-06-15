"""
Tool 3: Trust Scoring Tool
Aggregates all verification signals into a final trust score.

This is a LangChain @tool that can be used by LangChain agents.
"""

from langchain_core.tools import tool


@tool
def trust_scoring_tool(
    text_score: float,
    purchase_verified: bool,
    consistency_score: float,
    media_score: float = 0.85,
) -> dict:
    """
    Calculate the final trust score for a review by aggregating
    all verification signals with weighted scoring.
    
    Args:
        text_score: AI-generated probability (0-1, lower = more human)
        purchase_verified: Whether the purchase was verified
        consistency_score: Experience consistency score (0-1)
        media_score: Media authenticity score (0-1, optional)
    """
    # Weighted scoring algorithm
    base_score = 50
    
    # Purchase verification (25 points max)
    purchase_points = 25 if purchase_verified else 0
    
    # Consistency score (20 points max)
    consistency_points = int(consistency_score * 20)
    
    # Text authenticity (20 points max — lower AI score = more points)
    text_points = int((1 - text_score) * 20)
    
    # Media authenticity (10 points max)
    media_points = int(media_score * 10)
    
    final_score = base_score + purchase_points + consistency_points + text_points + media_points
    final_score = max(0, min(100, final_score))
    
    # Determine trust level
    if final_score >= 80:
        trust_level = "High"
        recommendation = "Review appears trustworthy and verified"
        action = "approve"
    elif final_score >= 50:
        trust_level = "Medium"
        recommendation = "Review has some verification concerns"
        action = "review"
    else:
        trust_level = "Low"
        recommendation = "Review requires manual review or rejection"
        action = "reject"
    
    return {
        "final_trust_score": final_score,
        "trust_level": trust_level,
        "breakdown": {
            "purchase_points": purchase_points,
            "consistency_points": consistency_points,
            "text_authenticity_points": text_points,
            "media_points": media_points,
        },
        "recommendation": recommendation,
        "action": action,
    }
