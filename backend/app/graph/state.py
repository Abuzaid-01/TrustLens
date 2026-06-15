"""
LangGraph State Schema — Defines the typed state that flows through all graph nodes.
Updated: Replaced text_auth with duplicate detection + reviewer behavior.
"""

from typing import TypedDict, Optional


class ReviewState(TypedDict, total=False):
    """State schema for the review verification LangGraph pipeline."""

    # ── User Input ──
    business_id: str
    bill_id: str
    review_text: str
    has_media: bool
    media_paths: list           # File paths of uploaded images

    # ── Intake Agent Results ──
    intake_result: dict
    run_purchase: bool
    run_consistency: bool
    run_duplicate: bool
    run_behavior: bool
    run_media_auth: bool

    # ── Verification Agent Results ──
    purchase_result: dict       # {purchase_verified, confidence, notes, order_details}
    consistency_result: dict    # {consistency_score, issues_found}
    duplicate_result: dict      # {is_duplicate, similarity_score, matched_review_id, flags}
    behavior_result: dict       # {behavior_score, risk_level, review_count, flags}
    media_auth_result: dict     # {media_authentic, authenticity_score, image_description, matches_review, match_score, flags}

    # ── Final Output ──
    trust_result: dict          # {final_trust_score, trust_level, breakdown, recommendation, action}

    # ── Persistence ──
    review_id: Optional[int]    # DB review ID after saving

    # ── Metadata ──
    error: Optional[str]
    agents_executed: list
