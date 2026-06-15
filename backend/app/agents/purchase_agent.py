"""
Purchase Verification Agent — Agent 2 of 6
NOW queries the REAL DATABASE to verify orders exist.
Uses Groq API Key 1 for LLM inference.
"""

import json
import traceback
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import GROQ_API_KEY_1, GROQ_MODEL, GROQ_FALLBACK_MODEL, GROQ_TEMPERATURE
from app.database.models import lookup_order

PURCHASE_SYSTEM_PROMPT = """You are a Purchase Verification Agent. You receive REAL database lookup results for a bill/order ID and must assess the verification status.

You will receive:
- order_id: The bill ID being verified
- db_lookup: The result from our database lookup (found/not found, order details, etc.)
- business_id: The business the review claims to be about

Your job:
1. If the order was NOT found in our database → purchase_verified = false
2. If the order WAS found but the business_id doesn't match → purchase_verified = false, flag mismatch
3. If the order WAS found and already reviewed → purchase_verified = false, flag duplicate
4. If the order WAS found, business matches, not yet reviewed → purchase_verified = true

Provide a confidence score:
- 0.95 if order found, business matches, not reviewed
- 0.3 if order found but business doesn't match
- 0.1 if order not found
- 0.0 if already reviewed

OUTPUT CONTRACT (STRICT):
Return ONLY this JSON object, no other text:
{
  "purchase_verified": true or false,
  "confidence": number between 0 and 1,
  "notes": "brief explanation",
  "order_details": "relevant order info if found, or null"
}

Rules:
- Output ONLY raw JSON, no markdown code fences
- Do NOT add extra fields"""


def _get_llm():
    """Create ChatGroq LLM instance with fallback."""
    try:
        return ChatGroq(
            api_key=GROQ_API_KEY_1,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=256,
        )
    except Exception:
        return ChatGroq(
            api_key=GROQ_API_KEY_1,
            model_name=GROQ_FALLBACK_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=256,
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


def run_purchase_agent(bill_id: str, business_id: str = "") -> dict:
    """
    Run the Purchase Verification Agent with REAL database lookup.
    """
    # Step 1: Look up the order in the real database
    db_result = lookup_order(bill_id)
    print(f"   📋 DB Lookup for '{bill_id}': found={db_result.get('found')}")

    # Step 2: Quick deterministic check (don't need LLM for simple cases)
    if not db_result.get("found"):
        print(f"   ❌ Order '{bill_id}' NOT found in database")
        return {
            "purchase_verified": False,
            "confidence": 0.1,
            "notes": f"Order ID '{bill_id}' not found in our system. This order does not exist in our database.",
            "order_details": None,
            "db_verified": True,
        }

    if db_result.get("already_reviewed"):
        print(f"   ⚠️ Order '{bill_id}' already reviewed")
        return {
            "purchase_verified": False,
            "confidence": 0.0,
            "notes": "A review has already been submitted for this order. Duplicate reviews are not allowed.",
            "order_details": None,
            "db_verified": True,
        }

    # Check business mismatch
    order_business = db_result.get("business_id", "")
    if business_id and order_business and business_id != order_business:
        print(f"   ⚠️ Business mismatch: expected '{business_id}', order belongs to '{order_business}'")
        return {
            "purchase_verified": False,
            "confidence": 0.2,
            "notes": f"Business mismatch: review claims '{business_id}' but order belongs to '{order_business}'.",
            "order_details": None,
            "db_verified": True,
        }

    # Step 3: Order found, verified, use LLM for rich response
    llm = _get_llm()

    human_message = json.dumps({
        "order_id": bill_id,
        "business_id": business_id,
        "db_lookup": db_result,
    })

    messages = [
        SystemMessage(content=PURCHASE_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]

    try:
        response = llm.invoke(messages)
        result = _parse_json_response(response.content)
        result["purchase_verified"] = True  # DB confirmed
        result["confidence"] = max(float(result.get("confidence", 0.95)), 0.9)
        result["db_verified"] = True

        print(f"✅ [Purchase Agent] Bill '{bill_id}' → VERIFIED (DB confirmed), confidence={result['confidence']}")
        return result

    except Exception as e:
        print(f"⚠️ [Purchase Agent] LLM failed but DB verified: {e}")
        # Fallback: DB already confirmed it's valid
        return {
            "purchase_verified": True,
            "confidence": 0.95,
            "notes": f"Order verified in database. Customer: {db_result.get('customer_name', 'N/A')}, Amount: ${db_result.get('amount', 0)}",
            "order_details": {
                "customer_name": db_result.get("customer_name"),
                "order_date": db_result.get("order_date"),
                "amount": db_result.get("amount"),
                "items": db_result.get("items"),
            },
            "db_verified": True,
        }
