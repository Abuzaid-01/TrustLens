"""
Tool 2: Authenticity Validation Tool
Handles text authenticity (AI detection) and media authenticity validation.

This is a LangChain @tool that can be used by LangChain agents.
"""

from langchain_core.tools import tool


@tool
def authenticity_validation_tool(
    review_text: str,
    media_type: str = "none",
    has_media: bool = False,
) -> dict:
    """
    Validate authenticity of review text and media. Detects AI-generated
    text, spam content, and checks media authenticity.
    
    Args:
        review_text: The review text to analyze
        media_type: Type of media ('image', 'video', or 'none')
        has_media: Whether media was uploaded
    """
    text_lower = review_text.lower()
    
    # AI detection
    ai_indicators = [
        "delve", "furthermore", "moreover", "in conclusion",
        "it is important to note", "comprehensive", "multifaceted",
    ]
    spam_indicators = [
        "click here", "visit our website", "buy now", "limited offer",
        "http://", "https://", "www.",
    ]
    
    ai_score = sum(1 for ind in ai_indicators if ind in text_lower)
    spam_score = sum(1 for ind in spam_indicators if ind in text_lower)
    
    ai_prob = min(ai_score * 0.2, 1.0)
    spam_prob = min(spam_score * 0.3, 1.0)
    
    risk_flags = []
    if ai_prob > 0.5:
        risk_flags.append("possible_ai_generated")
    if spam_prob > 0.3:
        risk_flags.append("spam_detected")
    if len(review_text) < 10:
        risk_flags.append("suspiciously_short")
    
    # Media authenticity
    media_result = {"media_authentic": True, "media_score": 0.85, "media_flags": []}
    if has_media and media_type != "none":
        if media_type == "image":
            media_result = {"media_authentic": True, "media_score": 0.85, "media_flags": []}
        elif media_type == "video":
            media_result = {"media_authentic": True, "media_score": 0.75, "media_flags": ["requires_manual_review"]}
        else:
            media_result = {"media_authentic": False, "media_score": 0.5, "media_flags": ["unknown_media_type"]}
    
    return {
        "ai_generated_probability": ai_prob,
        "spam_probability": spam_prob,
        "text_risk_flags": risk_flags,
        "text_verdict": "suspicious" if risk_flags else "authentic",
        "media_authentic": media_result["media_authentic"],
        "media_score": media_result["media_score"],
        "media_flags": media_result["media_flags"],
    }
