"""
Reviewer Behavior Agent — Agent 5 of 7
Analyzes the reviewer's submission patterns to detect suspicious activity
like review farms, bot-like behavior, or coordinated fake review campaigns.
Uses Groq API Key 2 for LLM inference.
"""

import json
import traceback
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import GROQ_API_KEY_2, GROQ_MODEL, GROQ_FALLBACK_MODEL, GROQ_TEMPERATURE
from app.database.models import get_customer_review_stats, get_reviews_by_customer_email, get_order


BEHAVIOR_SYSTEM_PROMPT = """You are a Reviewer Behavior Agent. Your task is to analyze a customer's review submission patterns and determine if their behavior is suspicious.

You will receive:
- customer_email: the reviewer's email
- current_order_id: the order being reviewed
- review_stats: { total_reviews, reviews_last_24h, avg_trust_score, recent_timestamps }
- past_reviews: list of their previous reviews (with scores and timestamps)

Suspicious behavior indicators:
- More than 3 reviews submitted in 24 hours (possible bot or review farm)
- Multiple reviews submitted within minutes of each other
- All reviews having suspiciously similar trust scores
- First-time reviewer with an extremely long or extremely short review (less suspicious alone, but note it)
- Reviewing businesses in wildly different categories in a short time span

Legitimate behavior indicators:
- First-time reviewer (no history — neutral, not suspicious)
- Reviews spread across days/weeks
- Varied trust scores across reviews
- Consistent reviewer with good track record

SCORING (behavior_score is 0.0 to 1.0):
- 0.8-1.0: Normal behavior, no concerns
- 0.5-0.8: Slightly unusual but not alarming
- 0.2-0.5: Suspicious patterns detected
- 0.0-0.2: Highly suspicious, likely fake/bot

OUTPUT CONTRACT (STRICT):
Return ONLY this JSON:
{
  "behavior_score": number between 0 and 1 (1.0 = trustworthy behavior),
  "risk_level": "low" or "medium" or "high",
  "review_count": integer,
  "flags": ["list of specific concerns found, empty if none"]
}

Rules:
- risk_level "low" if behavior_score >= 0.7
- risk_level "medium" if behavior_score 0.4-0.7
- risk_level "high" if behavior_score < 0.4
- For first-time reviewers with no history, default to behavior_score 0.85, risk_level "low", empty flags
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


def _compute_fallback(stats: dict) -> dict:
    """Deterministic fallback if LLM fails."""
    total = stats.get("total_reviews", 0)
    recent = stats.get("reviews_last_24h", 0)

    flags = []

    # First-time reviewer — neutral
    if total == 0:
        return {
            "behavior_score": 0.85,
            "risk_level": "low",
            "review_count": 0,
            "flags": [],
        }

    score = 1.0

    # Penalize rapid submissions
    if recent > 5:
        score -= 0.5
        flags.append(f"HIGH VOLUME: {recent} reviews in last 24 hours")
    elif recent > 3:
        score -= 0.3
        flags.append(f"ELEVATED VOLUME: {recent} reviews in last 24 hours")

    score = max(0.0, min(1.0, score))

    if score >= 0.7:
        risk = "low"
    elif score >= 0.4:
        risk = "medium"
    else:
        risk = "high"

    return {
        "behavior_score": round(score, 2),
        "risk_level": risk,
        "review_count": total,
        "flags": flags,
    }


def run_behavior_agent(bill_id: str) -> dict:
    """
    Run the Reviewer Behavior Agent.

    Args:
        bill_id: The order ID being reviewed (used to look up customer email)

    Returns:
        dict with behavior_score, risk_level, review_count, flags
    """
    print("   👤 Analyzing reviewer behavior patterns...")

    # Look up the customer email from the order
    order = get_order(bill_id)
    if not order:
        print("   ⚠️ Order not found — cannot analyze reviewer behavior")
        return {
            "behavior_score": 0.5,
            "risk_level": "medium",
            "review_count": 0,
            "flags": ["Order not found — behavior analysis limited"],
        }

    email = order.get("customer_email", "")
    if not email:
        print("   ⚠️ No customer email — defaulting to neutral")
        return {
            "behavior_score": 0.85,
            "risk_level": "low",
            "review_count": 0,
            "flags": [],
        }

    # Get customer stats and past reviews
    stats = get_customer_review_stats(email)
    past_reviews = get_reviews_by_customer_email(email)

    # If first-time reviewer, skip LLM — deterministic fast path
    if stats["total_reviews"] == 0:
        print(f"   ✅ First-time reviewer ({email}) — no prior history, behavior is clean")
        return {
            "behavior_score": 0.85,
            "risk_level": "low",
            "review_count": 0,
            "flags": [],
        }

    # Build context for LLM analysis
    context = {
        "customer_email": email,
        "current_order_id": bill_id,
        "review_stats": stats,
        "past_reviews": [
            {
                "order_id": r.get("order_id"),
                "trust_score": r.get("trust_score"),
                "trust_level": r.get("trust_level"),
                "action": r.get("action"),
                "created_at": r.get("created_at"),
                "review_preview": (r.get("review_text", "")[:80] + "...") if r.get("review_text") else "",
            }
            for r in past_reviews[:10]  # Limit to last 10
        ],
    }

    llm = _get_llm()
    messages = [
        SystemMessage(content=BEHAVIOR_SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(context, indent=2, default=str)),
    ]

    try:
        response = llm.invoke(messages)
        result = _parse_json_response(response.content)

        # Validate
        if "behavior_score" not in result:
            result["behavior_score"] = 0.5
        result["behavior_score"] = max(0.0, min(1.0, float(result["behavior_score"])))

        if "risk_level" not in result or result["risk_level"] not in ["low", "medium", "high"]:
            score = result["behavior_score"]
            result["risk_level"] = "low" if score >= 0.7 else ("medium" if score >= 0.4 else "high")

        if "review_count" not in result:
            result["review_count"] = stats["total_reviews"]

        if "flags" not in result:
            result["flags"] = []

        print(f"   ✅ [Behavior Agent] Score: {result['behavior_score']}, Risk: {result['risk_level']}, "
              f"Past reviews: {result['review_count']}")
        return result

    except Exception as e:
        print(f"   ❌ [Behavior Agent] Error: {e}, using fallback")
        traceback.print_exc()
        return _compute_fallback(stats)
