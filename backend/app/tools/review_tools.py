"""
Tool 1: Review Processing Tool
Handles review intake, purchase verification, and experience consistency.

This is a LangChain @tool that can be used by LangChain agents.
It also serves as the logic behind the /tools/review/* HTTP endpoints.
"""

from langchain_core.tools import tool


@tool
def review_processing_tool(
    business_id: str,
    bill_id: str,
    review_text: str,
    has_media: bool = False,
) -> dict:
    """
    Process a review submission: validate intake, verify purchase format,
    and check experience consistency. Returns structured analysis results.
    
    Args:
        business_id: The business identifier
        bill_id: The order/bill ID from receipt
        review_text: The review text content
        has_media: Whether media was uploaded
    """
    # Purchase format validation
    purchase_valid = (
        len(bill_id) >= 8
        and any(c.isalpha() for c in bill_id)
        and any(c.isdigit() for c in bill_id)
        and bill_id.lower() not in ["test", "12345", "fake"]
    )
    
    # Consistency quick-check
    word_count = len(review_text.split())
    exaggerated = ["best ever", "worst ever", "perfect", "terrible", "amazing", "horrible"]
    exag_count = sum(1 for w in exaggerated if w in review_text.lower())
    
    if word_count < 10:
        consistency = 0.3
    elif exag_count > 2:
        consistency = 0.4
    elif word_count > 50 and exag_count == 0:
        consistency = 0.9
    else:
        consistency = 0.7
    
    return {
        "status": "accepted",
        "review_id": f"rev_{bill_id}",
        "purchase_verified": purchase_valid,
        "purchase_confidence": 0.85 if purchase_valid else 0.15,
        "consistency_score": consistency,
        "word_count": word_count,
        "exaggeration_flags": exag_count,
        "next_steps": ["authenticity_validation", "trust_scoring"],
    }
