"""
Trust Score Agent — Agent 7 of 7
Computes the final trust score by aggregating all verification signals.
Uses Groq API Key 3 for LLM inference.

Updated: Replaced text_authenticity with duplicate_detection + reviewer_behavior.
Scoring: When no media is uploaded, media_points = 0 and the score is
normalized to a 0-100 scale.
"""

import json
import traceback
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import GROQ_API_KEY_3, GROQ_MODEL, GROQ_FALLBACK_MODEL, GROQ_TEMPERATURE

TRUST_SCORE_SYSTEM_PROMPT = """You are a Trust Score Agent. Your role is to compute a final trust score (0-100) for a review based on structured outputs from previous verification agents.

You will receive these signals:
- purchase_verified (boolean): Whether the purchase was verified via bill ID
- purchase_confidence (number 0-1): Confidence in purchase verification
- consistency_score (number 0-1): How consistent the review is with actual purchased items
- consistency_issues (array): Issues found by consistency agent
- is_duplicate (boolean): Whether the review text is a duplicate/copy of a past review
- similarity_score (number 0-1): How similar the review is to the best-matching past review
- duplicate_flags (array): Specific duplicate/plagiarism concerns
- behavior_score (number 0-1): Reviewer behavior trustworthiness (1.0 = very trustworthy)
- behavior_risk_level (string): "low", "medium", or "high"
- behavior_flags (array): Specific behavior concerns
- has_media (boolean): Whether the reviewer uploaded any images
- media_authentic (boolean or null): Whether media is authentic (null if no media)
- media_authenticity_score (number 0-1): Media authenticity confidence

IMPORTANT SCORING RULES:

**When has_media is TRUE** (reviewer uploaded images):
  Max possible = 100 points
  1. Purchase verification: 25 points if verified, 0 if not
  2. Consistency: consistency_score × 25 points (0-25 range)
  3. Duplicate detection: 15 points if NOT duplicate (similarity < 0.5), scale down if similar, 0 if duplicate
  4. Reviewer behavior: behavior_score × 15 points (0-15 range)
  5. Media verification: 20 points if authentic AND matches review, 12 if authentic but uncertain match, 0 if not authentic
  6. Clamp to 0-100

**When has_media is FALSE** (no images uploaded):
  Max possible = 100 points (media excluded, others scaled up)
  1. Purchase verification: 30 points if verified, 0 if not
  2. Consistency: consistency_score × 30 points (0-30 range)
  3. Duplicate detection: 20 points if NOT duplicate (similarity < 0.5), scale down based on similarity, 0 if duplicate
  4. Reviewer behavior: behavior_score × 20 points (0-20 range)
  5. Media: 0 points (N/A — no media to verify)
  6. Clamp to 0-100

Trust levels:
- >= 75: "High" → "Review appears trustworthy and verified" → action: "approve"
- >= 45: "Medium" → "Review has some verification concerns" → action: "review"  
- < 45: "Low" → "Review requires manual review or rejection" → action: "reject"

OUTPUT CONTRACT (STRICT):
Return ONLY this JSON object:
{
  "final_trust_score": integer 0-100,
  "trust_level": "High" or "Medium" or "Low",
  "breakdown": {
    "purchase_points": integer,
    "consistency_points": integer,
    "duplicate_points": integer,
    "behavior_points": integer,
    "media_points": integer
  },
  "recommendation": "string explanation",
  "action": "approve" or "review" or "reject"
}

Rules:
- Calculate scores using the EXACT algorithm above
- If is_duplicate is true, duplicate_points MUST be 0
- If has_media is false, media_points MUST be 0
- Keys must match exactly
- Do NOT add extra fields
- Output ONLY raw JSON, no markdown code fences"""


def _get_llm():
    """Create ChatGroq LLM instance with fallback."""
    try:
        return ChatGroq(
            api_key=GROQ_API_KEY_3,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=512,
        )
    except Exception:
        return ChatGroq(
            api_key=GROQ_API_KEY_3,
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


def _compute_fallback_score(trust_input: dict) -> dict:
    """Deterministic fallback scoring if LLM fails."""
    purchase_verified = trust_input.get("purchase_verified", False)
    consistency_score = float(trust_input.get("consistency_score", 0.5))
    is_duplicate = trust_input.get("is_duplicate", False)
    similarity_score = float(trust_input.get("similarity_score", 0.0))
    behavior_score = float(trust_input.get("behavior_score", 0.85))
    has_media = trust_input.get("has_media", False)
    media_authentic = trust_input.get("media_authentic")

    if has_media:
        # With media: 25 + 25 + 15 + 15 + 20 = 100
        purchase_pts = 25 if purchase_verified else 0
        consistency_pts = int(consistency_score * 25)
        dup_pts = 0 if is_duplicate else int((1 - min(similarity_score, 1.0)) * 15)
        behavior_pts = int(behavior_score * 15)
        media_pts = 20 if media_authentic else 0
    else:
        # No media: 30 + 30 + 20 + 20 + 0 = 100
        purchase_pts = 30 if purchase_verified else 0
        consistency_pts = int(consistency_score * 30)
        dup_pts = 0 if is_duplicate else int((1 - min(similarity_score, 1.0)) * 20)
        behavior_pts = int(behavior_score * 20)
        media_pts = 0

    final_score = max(0, min(100, purchase_pts + consistency_pts + dup_pts + behavior_pts + media_pts))

    if final_score >= 75:
        level, rec, action = "High", "Review appears trustworthy and verified", "approve"
    elif final_score >= 45:
        level, rec, action = "Medium", "Review has some verification concerns", "review"
    else:
        level, rec, action = "Low", "Review requires manual review or rejection", "reject"

    return {
        "final_trust_score": final_score,
        "trust_level": level,
        "breakdown": {
            "purchase_points": purchase_pts,
            "consistency_points": consistency_pts,
            "duplicate_points": dup_pts,
            "behavior_points": behavior_pts,
            "media_points": media_pts,
        },
        "recommendation": rec,
        "action": action,
    }


def run_trust_score_agent(trust_input: dict) -> dict:
    """
    Run the Trust Score Agent.

    Args:
        trust_input: dict with purchase_verified, consistency_score,
                     is_duplicate, similarity_score, behavior_score,
                     has_media, media_authentic, etc.

    Returns:
        dict with final_trust_score, trust_level, breakdown, recommendation, action
    """
    llm = _get_llm()

    human_message = json.dumps(trust_input, indent=2)

    messages = [
        SystemMessage(content=TRUST_SCORE_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]

    try:
        response = llm.invoke(messages)
        result = _parse_json_response(response.content)

        # Validate all required fields exist
        required = ["final_trust_score", "trust_level", "breakdown", "recommendation", "action"]
        for key in required:
            if key not in result:
                print(f"⚠️ [Trust Score Agent] Missing key '{key}', using fallback")
                return _compute_fallback_score(trust_input)

        # ENFORCE: if no media was uploaded, media_points MUST be 0
        has_media = trust_input.get("has_media", False)
        if not has_media and isinstance(result.get("breakdown"), dict):
            if result["breakdown"].get("media_points", 0) > 0:
                print("⚠️ [Trust Score Agent] LLM gave media points without media — correcting")
                result["breakdown"]["media_points"] = 0

        # ENFORCE: if duplicate detected, duplicate_points MUST be 0
        is_duplicate = trust_input.get("is_duplicate", False)
        if is_duplicate and isinstance(result.get("breakdown"), dict):
            if result["breakdown"].get("duplicate_points", 0) > 0:
                print("⚠️ [Trust Score Agent] LLM gave duplicate points for a duplicate — correcting")
                result["breakdown"]["duplicate_points"] = 0

        # Recalculate total from breakdown
        if isinstance(result.get("breakdown"), dict):
            bd = result["breakdown"]
            raw_total = (
                bd.get("purchase_points", 0)
                + bd.get("consistency_points", 0)
                + bd.get("duplicate_points", 0)
                + bd.get("behavior_points", 0)
                + bd.get("media_points", 0)
            )
            result["final_trust_score"] = max(0, min(100, raw_total))

        # Validate and clamp score
        result["final_trust_score"] = max(0, min(100, int(result["final_trust_score"])))

        # Validate trust_level
        if result["trust_level"] not in ["High", "Medium", "Low"]:
            score = result["final_trust_score"]
            result["trust_level"] = "High" if score >= 75 else ("Medium" if score >= 45 else "Low")

        # Validate action
        if result["action"] not in ["approve", "review", "reject"]:
            score = result["final_trust_score"]
            result["action"] = "approve" if score >= 75 else ("review" if score >= 45 else "reject")

        # Ensure breakdown exists with correct keys
        if not isinstance(result.get("breakdown"), dict):
            result["breakdown"] = _compute_fallback_score(trust_input)["breakdown"]

        print(f"✅ [Trust Score Agent] Score: {result['final_trust_score']}, Level: {result['trust_level']}, Action: {result['action']}, Media: {'yes' if has_media else 'no'}")
        return result

    except Exception as e:
        print(f"❌ [Trust Score Agent] Error: {e}, using deterministic fallback")
        traceback.print_exc()
        return _compute_fallback_score(trust_input)
