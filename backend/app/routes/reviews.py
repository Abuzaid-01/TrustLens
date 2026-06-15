"""
Reviews API — Review history and analytics endpoints.
"""

from fastapi import APIRouter
from app.database.models import get_reviews, get_reviews_by_business, get_review_media

router = APIRouter()


@router.get("/reviews")
async def list_reviews(limit: int = 50):
    """Get recent reviews with trust scores."""
    reviews = get_reviews(limit=limit)
    # Attach media info to each review
    for review in reviews:
        review["media"] = get_review_media(review["id"])
    return {"reviews": reviews, "count": len(reviews)}


@router.get("/reviews/{business_id}")
async def list_reviews_by_business(business_id: str):
    """Get all reviews for a specific business."""
    reviews = get_reviews_by_business(business_id)
    for review in reviews:
        review["media"] = get_review_media(review["id"])
    return {"business_id": business_id, "reviews": reviews, "count": len(reviews)}
