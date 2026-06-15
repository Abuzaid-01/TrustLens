"""
Review Submission API — Main endpoint for submitting reviews.
Now supports multipart form data with image uploads.
"""

import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.orchestrator.review_flow import run_review_flow
from app.core.config import UPLOADS_DIR

router = APIRouter()


@router.post("/review")
async def submit_review(
    business_id: str = Form(""),
    bill_id: str = Form(""),
    review_text: str = Form(""),
    has_media: bool = Form(False),
    images: list[UploadFile] = File(default=[]),
):
    """
    Submit a review for AI-powered trust verification.
    Accepts multipart form data with optional image uploads.
    """
    try:
        # Save uploaded images
        media_paths = []
        if images:
            for image in images:
                if image.filename and image.size and image.size > 0:
                    # Generate unique filename
                    ext = os.path.splitext(image.filename)[1] or ".jpg"
                    unique_name = f"{uuid.uuid4().hex}{ext}"
                    file_path = os.path.join(UPLOADS_DIR, unique_name)

                    # Save file
                    content = await image.read()
                    with open(file_path, "wb") as f:
                        f.write(content)

                    media_paths.append(file_path)
                    print(f"📁 Saved image: {unique_name} ({len(content)} bytes)")

        # Build input data
        data = {
            "business_id": business_id,
            "bill_id": bill_id,
            "review_text": review_text,
            "has_media": has_media or len(media_paths) > 0,
            "media_paths": media_paths,
        }

        result = run_review_flow(data)
        return result

    except Exception as e:
        print(f"❌ Review submission error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Review processing failed: {str(e)}",
        )
