"""
Experience Consistency Agent — Agent 3 of 6
Evaluates whether a review is realistic, internally consistent,
AND matches the actual purchase data from the database.
Uses Groq API Key 2 for LLM inference.
"""

import json
import traceback
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import GROQ_API_KEY_2, GROQ_MODEL, GROQ_FALLBACK_MODEL, GROQ_TEMPERATURE

CONSISTENCY_SYSTEM_PROMPT = """You are an Experience Consistency Agent for a review verification system.

Your job has TWO critical parts:

━━━ PART 1: PURCHASE-REVIEW MATCH (most important) ━━━
You receive the ACTUAL ORDER DETAILS from our database (business name, items purchased, category).
You MUST check if the review text actually talks about what was purchased.

CRITICAL mismatches that should result in score 0.05-0.2:
- Electronics store order + food review (e.g., Samsung order but reviewing "burgers and fries")
- Hotel order + restaurant review
- Ride-sharing order + product review
- Any review where the category of items discussed doesn't match the business type

PARTIAL mismatches (score 0.3-0.5):
- Right business category but wrong specific items mentioned
- Review mentions items not in the order

GOOD match (score 0.7-0.95):
- Review discusses the correct type of product/service
- Mentions some specific items from the actual order

━━━ PART 2: INTERNAL CONSISTENCY ━━━
- Detect exaggerated, unrealistic, or contradictory claims
- "best ever" or "worst ever" for mundane things are suspicious
- Very short reviews (<10 words) are suspicious (0.2-0.4)
- Contradictory statements should be flagged
- Multiple extreme superlatives should lower score

The PURCHASE-REVIEW MATCH check takes priority. Even if a review is internally consistent,
if it talks about completely different products than what was purchased, it MUST score very low (0.05-0.2).

OUTPUT CONTRACT (STRICT):
Return ONLY the following JSON object:
{
  "consistency_score": number between 0 and 1,
  "issues_found": ["string"]
}

Rules:
- Use EXACT key names as shown
- issues_found must be an array (empty array [] if no issues)
- If purchase-review mismatch detected, the FIRST issue MUST start with "MISMATCH:"
- Output ONLY raw JSON, no markdown code fences"""


def _get_llm():
    """Create ChatGroq LLM instance with fallback."""
    try:
        return ChatGroq(
            api_key=GROQ_API_KEY_2,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=512,
        )
    except Exception:
        return ChatGroq(
            api_key=GROQ_API_KEY_2,
            model_name=GROQ_FALLBACK_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=512,
        )


def _parse_json_response(text: str) -> dict:
    """Robustly parse JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise


def run_consistency_agent(review_text: str, purchase_context: dict = None) -> dict:
    """
    Run the Experience Consistency Agent.

    Args:
        review_text: The review text to analyze for consistency
        purchase_context: dict with business_name, business_category, items, amount
                         from the purchase verification step

    Returns:
        dict with consistency_score and issues_found
    """
    llm = _get_llm()

    # Build the human message with both review AND purchase context
    if purchase_context:
        human_message = f"""PURCHASE DATA FROM DATABASE:
- Business: {purchase_context.get('business_name', 'Unknown')}
- Business Category: {purchase_context.get('business_category', 'Unknown')}
- Items Purchased: {json.dumps(purchase_context.get('items', []))}
- Amount: ${purchase_context.get('amount', 'Unknown')}
- Order Date: {purchase_context.get('order_date', 'Unknown')}

REVIEW TEXT TO ANALYZE:
\"{review_text}\"

Check if this review is about the ACTUAL items/services purchased above. If the review talks about completely different products or services than what was purchased, flag it as a MISMATCH and give a very low score (0.05-0.2)."""
    else:
        human_message = f"""No purchase data available.

REVIEW TEXT TO ANALYZE:
\"{review_text}\"

Analyze for internal consistency only."""

    messages = [
        SystemMessage(content=CONSISTENCY_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]

    try:
        response = llm.invoke(messages)
        result = _parse_json_response(response.content)

        # Validate and clamp consistency_score
        if "consistency_score" not in result:
            result["consistency_score"] = 0.5
        result["consistency_score"] = max(0.0, min(1.0, float(result["consistency_score"])))

        if "issues_found" not in result:
            result["issues_found"] = []
        if not isinstance(result["issues_found"], list):
            result["issues_found"] = [str(result["issues_found"])]

        print(f"✅ [Consistency Agent] Score: {result['consistency_score']}, Issues: {len(result['issues_found'])}")
        if result["issues_found"]:
            for issue in result["issues_found"][:3]:
                print(f"   ⚠️ {issue}")
        return result

    except Exception as e:
        print(f"❌ [Consistency Agent] Error: {e}")
        traceback.print_exc()
        # Fail-safe: basic heuristic
        word_count = len(review_text.split())
        exaggerated = ["best ever", "worst ever", "perfect", "terrible", "amazing", "horrible"]
        exag_count = sum(1 for w in exaggerated if w in review_text.lower())

        if word_count < 10:
            score = 0.3
        elif exag_count > 2:
            score = 0.4
        elif word_count > 50:
            score = 0.85
        else:
            score = 0.7

        return {
            "consistency_score": score,
            "issues_found": ["Fallback heuristic used"] + (["Excessive exaggeration"] if exag_count > 2 else []),
        }
