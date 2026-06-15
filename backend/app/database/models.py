"""
Database CRUD operations for the review verification system.
All functions work with sqlite3.Row objects for clean dict-like access.
"""

import json
import sqlite3
from typing import Optional
from app.database.db import get_db


# ══════════════════════════════════════════════════════════════
# BUSINESSES
# ══════════════════════════════════════════════════════════════

def get_business(business_id: str) -> Optional[dict]:
    """Get a business by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM businesses WHERE id = ?", (business_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_businesses() -> list[dict]:
    """Get all registered businesses."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM businesses ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════

def get_order(order_id: str) -> Optional[dict]:
    """Get an order by order_id."""
    conn = get_db()
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["items"] = json.loads(data.get("items", "[]"))
        return data
    return None


def lookup_order(order_id: str) -> dict:
    """
    Look up an order and return verification status.
    Used by the frontend for pre-submission validation and by the purchase agent.
    """
    order = get_order(order_id)

    if not order:
        return {
            "found": False,
            "order_id": order_id,
            "message": "Order not found in our system. Please check your order ID.",
        }

    if order.get("review_submitted"):
        return {
            "found": True,
            "already_reviewed": True,
            "order_id": order_id,
            "business_id": order["business_id"],
            "message": "A review has already been submitted for this order.",
        }

    # Get business name
    business = get_business(order["business_id"])

    return {
        "found": True,
        "already_reviewed": False,
        "order_id": order_id,
        "business_id": order["business_id"],
        "business_name": business["name"] if business else order["business_id"],
        "customer_name": order.get("customer_name", ""),
        "order_date": order.get("order_date", ""),
        "items": order.get("items", []),
        "amount": order.get("amount", 0),
        "message": "Order verified! You can submit your review.",
    }


def mark_order_reviewed(order_id: str):
    """Mark an order as reviewed so it can't be reviewed twice."""
    conn = get_db()
    conn.execute("UPDATE orders SET review_submitted = 1 WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()


def get_orders_by_business(business_id: str) -> list[dict]:
    """Get all orders for a business."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE business_id = ? ORDER BY order_date DESC",
        (business_id,),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        data = dict(r)
        data["items"] = json.loads(data.get("items", "[]"))
        results.append(data)
    return results


# ══════════════════════════════════════════════════════════════
# REVIEWS
# ══════════════════════════════════════════════════════════════

def save_review(
    order_id: str,
    business_id: str,
    review_text: str,
    trust_score: int,
    trust_level: str,
    action: str,
    breakdown: dict,
    agents_log: dict,
    has_media: bool = False,
) -> int:
    """Save a review and its trust score. Returns the review ID."""
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO reviews
           (order_id, business_id, review_text, trust_score, trust_level,
            action, breakdown, agents_log, has_media)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            order_id,
            business_id,
            review_text,
            trust_score,
            trust_level,
            action,
            json.dumps(breakdown),
            json.dumps(agents_log),
            1 if has_media else 0,
        ),
    )
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Mark the order as reviewed
    if order_id:
        mark_order_reviewed(order_id)

    return review_id


def get_reviews(limit: int = 50) -> list[dict]:
    """Get recent reviews with trust scores."""
    conn = get_db()
    rows = conn.execute(
        """SELECT r.*, b.name as business_name
           FROM reviews r
           LEFT JOIN businesses b ON r.business_id = b.id
           ORDER BY r.created_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        data = dict(r)
        data["breakdown"] = json.loads(data.get("breakdown", "{}"))
        data["agents_log"] = json.loads(data.get("agents_log", "{}"))
        results.append(data)
    return results


def get_reviews_by_business(business_id: str) -> list[dict]:
    """Get all reviews for a specific business."""
    conn = get_db()
    rows = conn.execute(
        """SELECT r.*, b.name as business_name
           FROM reviews r
           LEFT JOIN businesses b ON r.business_id = b.id
           WHERE r.business_id = ?
           ORDER BY r.created_at DESC""",
        (business_id,),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        data = dict(r)
        data["breakdown"] = json.loads(data.get("breakdown", "{}"))
        data["agents_log"] = json.loads(data.get("agents_log", "{}"))
        results.append(data)
    return results


# ══════════════════════════════════════════════════════════════
# REVIEW MEDIA
# ══════════════════════════════════════════════════════════════

def save_review_media(
    review_id: int,
    file_path: str,
    file_type: str,
    original_name: str,
    vision_analysis: dict = None,
    matches_review: bool = True,
    match_score: float = 0.0,
) -> int:
    """Save media metadata for a review. Returns the media ID."""
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO review_media
           (review_id, file_path, file_type, original_name,
            vision_analysis, matches_review, match_score)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            review_id,
            file_path,
            file_type,
            original_name,
            json.dumps(vision_analysis or {}),
            1 if matches_review else 0,
            match_score,
        ),
    )
    media_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return media_id


def get_review_media(review_id: int) -> list[dict]:
    """Get all media for a review."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM review_media WHERE review_id = ?",
        (review_id,),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        data = dict(r)
        data["vision_analysis"] = json.loads(data.get("vision_analysis", "{}"))
        results.append(data)
    return results


# ══════════════════════════════════════════════════════════════
# DUPLICATE DETECTION & REVIEWER BEHAVIOR QUERIES
# ══════════════════════════════════════════════════════════════

def get_all_review_texts() -> list[dict]:
    """Get all past review texts for duplicate/plagiarism comparison."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, order_id, business_id, review_text FROM reviews ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_reviews_by_customer_email(email: str) -> list[dict]:
    """Get all past reviews submitted by the same customer email."""
    conn = get_db()
    rows = conn.execute(
        """SELECT r.id, r.order_id, r.business_id, r.review_text,
                  r.trust_score, r.trust_level, r.action, r.created_at
           FROM reviews r
           JOIN orders o ON r.order_id = o.order_id
           WHERE o.customer_email = ?
           ORDER BY r.created_at DESC""",
        (email,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_review_stats(email: str) -> dict:
    """Get review statistics for a customer — count, timing, score distribution."""
    conn = get_db()

    # Total review count
    total = conn.execute(
        """SELECT COUNT(*) FROM reviews r
           JOIN orders o ON r.order_id = o.order_id
           WHERE o.customer_email = ?""",
        (email,),
    ).fetchone()[0]

    # Reviews in last 24 hours
    recent = conn.execute(
        """SELECT COUNT(*) FROM reviews r
           JOIN orders o ON r.order_id = o.order_id
           WHERE o.customer_email = ?
           AND r.created_at >= datetime('now', '-1 day')""",
        (email,),
    ).fetchone()[0]

    # Average trust score
    avg_row = conn.execute(
        """SELECT AVG(r.trust_score) FROM reviews r
           JOIN orders o ON r.order_id = o.order_id
           WHERE o.customer_email = ?""",
        (email,),
    ).fetchone()
    avg_score = round(avg_row[0], 1) if avg_row[0] is not None else None

    # Review timestamps for timing analysis
    timestamps = conn.execute(
        """SELECT r.created_at FROM reviews r
           JOIN orders o ON r.order_id = o.order_id
           WHERE o.customer_email = ?
           ORDER BY r.created_at DESC LIMIT 10""",
        (email,),
    ).fetchall()

    conn.close()

    return {
        "total_reviews": total,
        "reviews_last_24h": recent,
        "avg_trust_score": avg_score,
        "recent_timestamps": [t[0] for t in timestamps],
    }
