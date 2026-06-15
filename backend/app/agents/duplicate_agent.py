"""
Duplicate/Plagiarism Detection Agent — Agent 4 of 7
Checks if the review text is a duplicate or near-copy of any previously submitted review.
Uses deterministic string similarity (no LLM needed) for speed and reliability.
"""

from difflib import SequenceMatcher
from app.database.models import get_all_review_texts


# Common spam template fragments — instant flags
SPAM_TEMPLATES = [
    "click here",
    "visit our website",
    "buy now",
    "limited offer",
    "discount code",
    "earn money",
    "work from home",
    "100% guaranteed",
    "act now",
    "congratulations you have been selected",
]

# Similarity threshold for flagging
DUPLICATE_THRESHOLD = 0.70  # 70% similar = flagged
HIGH_SIMILARITY_THRESHOLD = 0.85  # 85% similar = very likely copy-paste


def _normalize_text(text: str) -> str:
    """Normalize text for comparison — lowercase, strip extra spaces."""
    return " ".join(text.lower().split())


def _check_spam_templates(review_text: str) -> list[str]:
    """Check for known spam template phrases."""
    text_lower = review_text.lower()
    return [phrase for phrase in SPAM_TEMPLATES if phrase in text_lower]


def _find_best_match(review_text: str, past_reviews: list[dict]) -> dict:
    """Find the most similar past review using SequenceMatcher."""
    normalized_new = _normalize_text(review_text)
    best_match = {"similarity": 0.0, "matched_review_id": None, "matched_text": ""}

    for past in past_reviews:
        past_text = past.get("review_text", "")
        if not past_text:
            continue

        normalized_past = _normalize_text(past_text)
        ratio = SequenceMatcher(None, normalized_new, normalized_past).ratio()

        if ratio > best_match["similarity"]:
            best_match = {
                "similarity": round(ratio, 3),
                "matched_review_id": past.get("id"),
                "matched_order_id": past.get("order_id", ""),
                "matched_business_id": past.get("business_id", ""),
                "matched_text_preview": past_text[:100] + "..." if len(past_text) > 100 else past_text,
            }

    return best_match


def run_duplicate_agent(review_text: str) -> dict:
    """
    Run the Duplicate/Plagiarism Detection Agent.

    Args:
        review_text: The review text to check for duplicates

    Returns:
        dict with is_duplicate, similarity_score, matched_review_id, flags
    """
    print("   🔍 Checking for duplicate/plagiarized reviews...")

    flags = []

    # 1. Check for spam template phrases
    spam_hits = _check_spam_templates(review_text)
    if spam_hits:
        flags.append(f"SPAM: Contains known spam phrases: {', '.join(spam_hits)}")

    # 2. Compare against all past reviews
    past_reviews = get_all_review_texts()

    if not past_reviews:
        print("   ℹ️ No past reviews in database — skipping similarity check")
        return {
            "is_duplicate": len(spam_hits) > 0,
            "similarity_score": 0.0,
            "matched_review_id": None,
            "flags": flags,
            "total_compared": 0,
        }

    best_match = _find_best_match(review_text, past_reviews)
    similarity = best_match["similarity"]

    # 3. Determine duplicate status
    is_duplicate = False

    if similarity >= HIGH_SIMILARITY_THRESHOLD:
        is_duplicate = True
        flags.append(
            f"DUPLICATE: {int(similarity * 100)}% match with review #{best_match['matched_review_id']} "
            f"(order {best_match.get('matched_order_id', 'unknown')})"
        )
    elif similarity >= DUPLICATE_THRESHOLD:
        is_duplicate = True
        flags.append(
            f"SIMILAR: {int(similarity * 100)}% overlap with review #{best_match['matched_review_id']} — "
            f"possible copy-paste with minor edits"
        )

    if spam_hits:
        is_duplicate = True

    result = {
        "is_duplicate": is_duplicate,
        "similarity_score": similarity,
        "matched_review_id": best_match.get("matched_review_id"),
        "flags": flags,
        "total_compared": len(past_reviews),
    }

    status = "🚨 DUPLICATE DETECTED" if is_duplicate else "✅ Original content"
    print(f"   {status} — similarity: {similarity:.1%}, compared against {len(past_reviews)} reviews")

    return result
