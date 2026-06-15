"""
Tool endpoints that match the OpenAPI schemas
These are the 3 custom tools required for the hackathon
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os
from datetime import date

router = APIRouter()


# ═══════════════════════════════════════════════════════════
# TOOL 1: REVIEW PROCESSING TOOL
# ═══════════════════════════════════════════════════════════

class ReviewIntakeRequest(BaseModel):
    business_id: str
    bill_id: str
    review_text: str
    visit_date: Optional[str] = None


class ConsistencyCheckRequest(BaseModel):
    review_text: str
    business_type: str


class PurchaseVerificationRequest(BaseModel):
    bill_id: str
    business_id: str


@router.post("/review/intake")
def submit_review_tool(data: ReviewIntakeRequest):
    """
    Tool endpoint for review intake
    Stores review and initiates verification pipeline
    """
    return {
        "status": "accepted",
        "review_id": f"rev_{data.bill_id}",
        "message": "Review submitted for verification",
        "next_steps": [
            "purchase_verification",
            "consistency_check",
            "authenticity_validation"
        ]
    }


@router.post("/review/consistency-check")
def check_consistency_tool(data: ConsistencyCheckRequest):
    """
    Tool endpoint for experience consistency validation
    Analyzes if review matches expected business patterns
    """
    # Simple heuristic-based consistency check
    review_lower = data.review_text.lower()
    
    # Check for exaggeration keywords
    exaggeration_keywords = ["best ever", "worst ever", "perfect", "terrible", "amazing", "horrible"]
    exaggeration_count = sum(1 for keyword in exaggeration_keywords if keyword in review_lower)
    
    # Check review length
    word_count = len(data.review_text.split())
    
    # Calculate consistency score
    if word_count < 10:
        consistency_score = 0.3  # Too short, suspicious
    elif exaggeration_count > 2:
        consistency_score = 0.4  # Too many exaggerations
    elif word_count > 50 and exaggeration_count == 0:
        consistency_score = 0.9  # Detailed and balanced
    else:
        consistency_score = 0.7  # Normal review
    
    return {
        "consistency_score": consistency_score,
        "word_count": word_count,
        "exaggeration_flags": exaggeration_count,
        "verdict": "consistent" if consistency_score > 0.6 else "suspicious"
    }


@router.post("/verify/purchase")
def verify_purchase_tool(data: PurchaseVerificationRequest):
    """
    Tool endpoint for purchase verification
    Validates if bill ID is legitimate
    """
    bill_id = data.bill_id
    
    # Simple validation logic for demo
    # In production, this would check against a database
    is_valid = (
        len(bill_id) >= 8 and
        any(char.isdigit() for char in bill_id) and
        any(char.isalpha() for char in bill_id) and
        bill_id not in ["test", "12345", "fake"]
    )
    
    return {
        "purchase_verified": is_valid,
        "bill_id": bill_id,
        "confidence": 0.85 if is_valid else 0.15,
        "verification_method": "format_validation",
        "notes": "Valid bill format" if is_valid else "Suspicious bill format"
    }


# ═══════════════════════════════════════════════════════════
# TOOL 2: AUTHENTICITY VALIDATION TOOL
# ═══════════════════════════════════════════════════════════

class TextAuthRequest(BaseModel):
    review_text: str


class MediaAuthRequest(BaseModel):
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    media_type: str  # 'image' or 'video'


@router.post("/auth/text")
def validate_text_authenticity_tool(data: TextAuthRequest):
    """
    Tool endpoint for text authenticity validation
    Detects AI-generated or spam content
    """
    text = data.review_text
    
    # Simple AI detection heuristics for demo
    ai_indicators = [
        "delve", "furthermore", "moreover", "in conclusion",
        "it is important to note", "comprehensive", "multifaceted"
    ]
    
    spam_indicators = [
        "click here", "visit our website", "buy now", "limited offer",
        "http://", "https://", "www."
    ]
    
    text_lower = text.lower()
    
    # Calculate probabilities
    ai_score = sum(1 for indicator in ai_indicators if indicator in text_lower)
    spam_score = sum(1 for indicator in spam_indicators if indicator in text_lower)
    
    ai_generated_probability = min(ai_score * 0.2, 1.0)
    spam_probability = min(spam_score * 0.3, 1.0)
    
    risk_flags = []
    if ai_generated_probability > 0.5:
        risk_flags.append("possible_ai_generated")
    if spam_probability > 0.3:
        risk_flags.append("spam_detected")
    if len(text) < 10:
        risk_flags.append("suspiciously_short")
    
    return {
        "ai_generated_probability": ai_generated_probability,
        "spam_probability": spam_probability,
        "text_risk_flags": risk_flags,
        "verdict": "suspicious" if risk_flags else "authentic"
    }


@router.post("/auth/media")
def validate_media_authenticity_tool(data: MediaAuthRequest):
    """
    Tool endpoint for media authenticity validation
    Uses local heuristics for demo media authenticity checks.
    """
    # For demo purposes, we'll simulate media validation
    # In production, this would call the same vision agent used by the main pipeline.
    
    # Simulate different authenticity scores based on media type
    if data.media_type == "image":
        authenticity_score = 0.85
        tampering_detected = False
        risk_flags = []
    elif data.media_type == "video":
        authenticity_score = 0.75
        tampering_detected = False
        risk_flags = ["requires_manual_review"]
    else:
        authenticity_score = 0.5
        tampering_detected = True
        risk_flags = ["unknown_media_type"]
    
    return {
        "media_authenticity_score": authenticity_score,
        "tampering_detected": tampering_detected,
        "media_risk_flags": risk_flags,
        "analysis_method": "demo_media_heuristics",
        "verdict": "authentic" if authenticity_score > 0.7 else "suspicious"
    }


# ═══════════════════════════════════════════════════════════
# TOOL 3: TRUST SCORING TOOL
# ═══════════════════════════════════════════════════════════

class TrustScoreRequest(BaseModel):
    text_score: float
    media_score: Optional[float] = None
    purchase_verified: bool
    consistency_score: float


@router.post("/trust/score")
def generate_trust_score_tool(data: TrustScoreRequest):
    """
    Tool endpoint for final trust score calculation
    Aggregates all verification signals
    """
    # Weighted scoring algorithm
    base_score = 50
    
    # Purchase verification (25 points)
    purchase_points = 25 if data.purchase_verified else 0
    
    # Consistency score (20 points)
    consistency_points = int(data.consistency_score * 20)
    
    # Text authenticity (20 points)
    # Lower text_score means more human-like (good)
    text_points = int((1 - data.text_score) * 20)
    
    # Media authenticity (10 points, optional)
    media_points = 0
    if data.media_score is not None:
        media_points = int(data.media_score * 10)
    
    final_score = base_score + purchase_points + consistency_points + text_points + media_points
    final_score = min(max(final_score, 0), 100)  # Clamp to 0-100
    
    # Determine trust level
    if final_score >= 80:
        trust_level = "High"
        recommendation = "Review appears trustworthy and verified"
    elif final_score >= 50:
        trust_level = "Medium"
        recommendation = "Review has some verification concerns"
    else:
        trust_level = "Low"
        recommendation = "Review requires manual review or rejection"
    
    return {
        "final_trust_score": final_score,
        "trust_level": trust_level,
        "breakdown": {
            "purchase_points": purchase_points,
            "consistency_points": consistency_points,
            "text_authenticity_points": text_points,
            "media_points": media_points
        },
        "recommendation": recommendation,
        "action": "approve" if final_score >= 70 else "review" if final_score >= 50 else "reject"
    }


# ═══════════════════════════════════════════════════════════
# MEDIA UPLOAD ENDPOINT
# ═══════════════════════════════════════════════════════════

@router.post("/media/upload")
async def upload_media(file: UploadFile = File(...)):
    """
    Upload media for later authenticity analysis.
    """
    # For now, this stores metadata for the demo tool endpoint.
    
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    media_id = f"media_{file.filename}_{file_size}"
    
    return {
        "media_id": media_id,
        "filename": file.filename,
        "size": file_size,
        "content_type": file.content_type,
        "status": "uploaded",
        "message": "Media uploaded for authenticity analysis",
        "next_step": "Call /auth/media with this media_id for validation"
    }
