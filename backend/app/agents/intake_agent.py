"""
Review Intake Agent — Agent 1 of 7
Analyzes incoming review data and decides which verification agents to activate.
Uses Groq API Key 1 for LLM inference.
"""

import json
import traceback
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import GROQ_API_KEY_1, GROQ_MODEL, GROQ_FALLBACK_MODEL, GROQ_TEMPERATURE

INTAKE_SYSTEM_PROMPT = """You are a Review Intake Agent. Your role:
- Receive structured review data from the backend
- Understand the review context
- Decide whether additional verification steps are required

You will receive the following inputs:
- business_id (string)
- bill_id (string)
- review_text (string)
- has_media (boolean)

You MUST:
- Analyze the review text and metadata
- Decide which checks are required based on the content

Decision guidelines:
- needs_purchase_verification: TRUE if a bill_id is provided and non-empty
- needs_experience_consistency_check: TRUE if the review text is longer than 5 words
- needs_duplicate_check: TRUE always (every review should be checked for plagiarism/duplicates)
- needs_behavior_check: TRUE always (every reviewer's patterns should be analyzed)
- needs_media_authenticity_check: TRUE only if has_media is true

You MUST NOT:
- Ask follow-up questions
- Validate authenticity yourself
- Judge quality
- Calculate scores

OUTPUT CONTRACT (STRICT):
Return ONLY this JSON object, no other text:
{
  "needs_purchase_verification": true or false,
  "needs_experience_consistency_check": true or false,
  "needs_duplicate_check": true or false,
  "needs_behavior_check": true or false,
  "needs_media_authenticity_check": true or false,
  "summary": "short summary of the review"
}

Rules:
- Keys must match exactly (case-sensitive)
- Do NOT rename keys
- Do NOT add extra fields
- Do NOT include any text outside JSON
- Output ONLY raw JSON, no markdown code fences"""


def _get_llm():
    """Create ChatGroq LLM instance with fallback."""
    try:
        return ChatGroq(
            api_key=GROQ_API_KEY_1,
            model_name=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=512,
        )
    except Exception:
        return ChatGroq(
            api_key=GROQ_API_KEY_1,
            model_name=GROQ_FALLBACK_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=512,
        )


def _parse_json_response(text: str) -> dict:
    """Robustly parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise


def run_intake_agent(input_data: dict) -> dict:
    """
    Run the Review Intake Agent on the given input data.
    
    Args:
        input_data: dict with business_id, bill_id, review_text, has_media
    
    Returns:
        dict with needs_* flags and summary
    """
    llm = _get_llm()
    
    human_message = json.dumps(input_data, indent=2)
    
    messages = [
        SystemMessage(content=INTAKE_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]
    
    try:
        response = llm.invoke(messages)
        result = _parse_json_response(response.content)
        
        # Validate expected keys exist
        expected_keys = [
            "needs_purchase_verification",
            "needs_experience_consistency_check",
            "needs_duplicate_check",
            "needs_behavior_check",
            "needs_media_authenticity_check",
        ]
        for key in expected_keys:
            if key not in result:
                result[key] = True  # Default to running the check
        
        if "summary" not in result:
            result["summary"] = "Review submitted for verification"
        
        print(f"✅ [Intake Agent] Result: {json.dumps(result, indent=2)}")
        return result
        
    except Exception as e:
        print(f"❌ [Intake Agent] Error: {e}")
        traceback.print_exc()
        # Fail-safe: run all checks
        return {
            "needs_purchase_verification": bool(input_data.get("bill_id")),
            "needs_experience_consistency_check": True,
            "needs_duplicate_check": True,
            "needs_behavior_check": True,
            "needs_media_authenticity_check": bool(input_data.get("has_media")),
            "summary": "Intake agent fallback — running all checks",
        }
