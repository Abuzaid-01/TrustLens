"""
Media Authenticity Agent — Agent 5 of 6
NOW uses Groq Llama 4 Scout VISION MODEL to actually analyze uploaded images.
Compares image content with review text to detect mismatches.
Uses Groq API Key 3 for LLM inference.
"""

import json
import base64
import traceback
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import (
    GROQ_API_KEY_3, GROQ_MODEL, GROQ_FALLBACK_MODEL,
    GROQ_VISION_MODEL, GROQ_TEMPERATURE,
)

MEDIA_VISION_PROMPT = """You are a Media Validation Agent with VISION capabilities. You can SEE uploaded images.

Your task:
1. Describe what you see in the image (be specific)
2. Compare the image content with the review text
3. Determine if the image supports/matches the review

Scoring:
- 0.8-1.0: Image clearly matches the review (e.g., food photo matches restaurant review)
- 0.5-0.7: Image is somewhat related but not clearly matching
- 0.2-0.4: Image doesn't match the review context
- 0.0-0.1: Image is clearly unrelated, stock photo, or meme

Also check for:
- AI-generated images (overly perfect, weird artifacts)
- Stock photos (watermarks, generic content)
- Screenshots of other reviews (fake social proof)
- Completely unrelated content

OUTPUT CONTRACT (STRICT):
Return ONLY this JSON object:
{
  "media_authentic": true or false,
  "authenticity_score": number between 0 and 1,
  "image_description": "what you see in the image",
  "matches_review": true or false,
  "match_score": number between 0 and 1,
  "match_explanation": "why does or doesn't the image match the review",
  "flags": ["array of concerns, empty if none"]
}

Rules:
- Output ONLY raw JSON, no markdown code fences
- Be specific about what you see in the image"""

MEDIA_TEXT_ONLY_PROMPT = """You are a Media Validation Agent. You evaluate media authenticity claims for review verification.

Since you cannot directly view the images, you analyze:
- Whether the user claims to have media (has_media flag)
- The context of the review — does it reference specific visual details?
- Whether media claims are consistent with the review text

OUTPUT CONTRACT (STRICT):
Return ONLY this JSON object:
{
  "media_authentic": true or false,
  "authenticity_score": number between 0 and 1,
  "image_description": "unable to analyze - vision not available",
  "matches_review": true or false,
  "match_score": number between 0 and 1,
  "match_explanation": "contextual analysis only",
  "flags": ["array of concerns"]
}

Rules:
- Output ONLY raw JSON, no markdown code fences"""


def _get_vision_llm():
    """Create ChatGroq LLM with vision model."""
    return ChatGroq(
        api_key=GROQ_API_KEY_3,
        model_name=GROQ_VISION_MODEL,
        temperature=GROQ_TEMPERATURE,
        max_tokens=512,
    )


def _get_text_llm():
    """Create ChatGroq LLM for text-only fallback."""
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


def _encode_image_base64(file_path: str) -> str:
    """Read an image file and return base64-encoded string."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_image_mime_type(file_path: str) -> str:
    """Get MIME type from file extension."""
    ext = Path(file_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_map.get(ext, "image/jpeg")


def run_media_auth_agent(
    review_text: str,
    has_media: bool,
    media_paths: list[str] = None,
) -> dict:
    """
    Run the Media Authenticity Agent.
    If media_paths are provided, uses VISION model to actually analyze images.
    """
    # If no media, skip entirely
    if not has_media or not media_paths:
        print("✅ [Media Agent] No media uploaded — skipping analysis")
        return {
            "media_authentic": True,
            "authenticity_score": 0.85,
            "image_description": "No media uploaded",
            "matches_review": True,
            "match_score": 1.0,
            "match_explanation": "No media to verify",
            "flags": [],
        }

    # Try vision analysis for each image
    all_results = []
    for i, image_path in enumerate(media_paths[:3]):  # Max 3 images
        print(f"   📷 Analyzing image {i+1}: {Path(image_path).name}")
        result = _analyze_single_image(review_text, image_path)
        all_results.append(result)

    # Aggregate results from all images
    if not all_results:
        return {
            "media_authentic": True,
            "authenticity_score": 0.75,
            "image_description": "No images could be analyzed",
            "matches_review": True,
            "match_score": 0.5,
            "match_explanation": "Unable to analyze images",
            "flags": ["analysis_failed"],
        }

    # Average scores across all images
    avg_auth = sum(r.get("authenticity_score", 0.5) for r in all_results) / len(all_results)
    avg_match = sum(r.get("match_score", 0.5) for r in all_results) / len(all_results)
    all_flags = []
    descriptions = []
    for r in all_results:
        all_flags.extend(r.get("flags", []))
        desc = r.get("image_description", "")
        if desc:
            descriptions.append(desc)

    final = {
        "media_authentic": avg_auth > 0.4,
        "authenticity_score": round(avg_auth, 2),
        "image_description": " | ".join(descriptions) if descriptions else "Images analyzed",
        "matches_review": avg_match > 0.4,
        "match_score": round(avg_match, 2),
        "match_explanation": all_results[0].get("match_explanation", ""),
        "flags": list(set(all_flags)),
        "per_image_results": all_results,
    }

    print(f"✅ [Media Agent] Authentic: {final['media_authentic']}, Match: {final['match_score']}")
    return final


def _analyze_single_image(review_text: str, image_path: str) -> dict:
    """Analyze a single image with the vision model."""
    try:
        # Encode image
        image_b64 = _encode_image_base64(image_path)
        mime_type = _get_image_mime_type(image_path)

        llm = _get_vision_llm()

        # Build multimodal message with image
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"Analyze this uploaded image for a review verification system.\n\nThe review text says: \"{review_text}\"\n\nAnalyze the image and determine if it matches/supports the review. Follow the output contract exactly.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_b64}",
                    },
                },
            ]
        )

        messages = [
            SystemMessage(content=MEDIA_VISION_PROMPT),
            message,
        ]

        response = llm.invoke(messages)
        result = _parse_json_response(response.content)

        # Validate fields
        result.setdefault("media_authentic", True)
        result.setdefault("authenticity_score", 0.7)
        result.setdefault("image_description", "Image analyzed")
        result.setdefault("matches_review", True)
        result.setdefault("match_score", 0.5)
        result.setdefault("match_explanation", "")
        result.setdefault("flags", [])

        result["authenticity_score"] = max(0.0, min(1.0, float(result["authenticity_score"])))
        result["match_score"] = max(0.0, min(1.0, float(result["match_score"])))

        print(f"   🔍 Vision result: auth={result['authenticity_score']}, match={result['match_score']}")
        return result

    except Exception as e:
        print(f"   ⚠️ Vision analysis failed: {e}, falling back to text-only")
        traceback.print_exc()
        return _analyze_text_only(review_text)


def _analyze_text_only(review_text: str) -> dict:
    """Fallback: text-only analysis when vision isn't available."""
    try:
        llm = _get_text_llm()

        messages = [
            SystemMessage(content=MEDIA_TEXT_ONLY_PROMPT),
            HumanMessage(content=f"Review text: \"{review_text}\"\nhas_media: true"),
        ]

        response = llm.invoke(messages)
        result = _parse_json_response(response.content)
        result.setdefault("media_authentic", True)
        result.setdefault("authenticity_score", 0.7)
        result.setdefault("flags", ["vision_unavailable_text_analysis_only"])
        return result

    except Exception as e:
        print(f"   ❌ Text-only fallback also failed: {e}")
        return {
            "media_authentic": True,
            "authenticity_score": 0.6,
            "image_description": "Analysis unavailable",
            "matches_review": True,
            "match_score": 0.5,
            "match_explanation": "Fallback mode — unable to analyze",
            "flags": ["analysis_failed_fallback"],
        }
