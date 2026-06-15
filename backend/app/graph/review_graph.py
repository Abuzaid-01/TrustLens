"""
LangGraph Review Graph — The core state machine orchestrating all 7 agents.
Updated: Replaced text_auth with duplicate_detection + reviewer_behavior.
Pipeline: intake → purchase → consistency → duplicate → behavior → media_auth → trust_score → save_review
"""

import json
import traceback
from langgraph.graph import StateGraph, END

from app.graph.state import ReviewState
from app.agents.intake_agent import run_intake_agent
from app.agents.purchase_agent import run_purchase_agent
from app.agents.consistency_agent import run_consistency_agent
from app.agents.duplicate_agent import run_duplicate_agent
from app.agents.behavior_agent import run_behavior_agent
from app.agents.media_auth_agent import run_media_auth_agent
from app.agents.trust_score_agent import run_trust_score_agent
from app.database.models import save_review, save_review_media


# ══════════════════════════════════════════════════════════════
# GRAPH NODES
# ══════════════════════════════════════════════════════════════

def intake_node(state: ReviewState) -> dict:
    """Node 1: Review Intake — analyze review and decide what to check."""
    print("\n🔵 ━━━ Node 1: Review Intake Agent ━━━")

    input_data = {
        "business_id": state.get("business_id", ""),
        "bill_id": state.get("bill_id", ""),
        "review_text": state.get("review_text", ""),
        "has_media": state.get("has_media", False),
    }

    result = run_intake_agent(input_data)

    return {
        "intake_result": result,
        "run_purchase": result.get("needs_purchase_verification", True),
        "run_consistency": result.get("needs_experience_consistency_check", True),
        "run_duplicate": result.get("needs_duplicate_check", True),
        "run_behavior": result.get("needs_behavior_check", True),
        "run_media_auth": result.get("needs_media_authenticity_check", False),
        "agents_executed": ["review_intake"],
    }


def purchase_node(state: ReviewState) -> dict:
    """Node 2: Purchase Verification — validate bill ID against DATABASE."""
    print("\n🟡 ━━━ Node 2: Purchase Verification Agent ━━━")

    if not state.get("run_purchase", False):
        print("   ⏭️ Skipped (not required by intake)")
        return {
            "purchase_result": {
                "purchase_verified": False,
                "confidence": 0.0,
                "notes": "Skipped — not required",
            },
        }

    result = run_purchase_agent(
        bill_id=state.get("bill_id", ""),
        business_id=state.get("business_id", ""),
    )

    agents = state.get("agents_executed", []) + ["purchase_verification"]
    return {"purchase_result": result, "agents_executed": agents}


def consistency_node(state: ReviewState) -> dict:
    """Node 3: Experience Consistency — check if review matches purchase AND is realistic."""
    print("\n🟠 ━━━ Node 3: Experience Consistency Agent ━━━")

    if not state.get("run_consistency", False):
        print("   ⏭️ Skipped (not required by intake)")
        return {
            "consistency_result": {
                "consistency_score": 0.5,
                "issues_found": [],
            },
        }

    # Build purchase context from the purchase agent result + DB lookup
    purchase = state.get("purchase_result", {})
    order_details = purchase.get("order_details")
    purchase_context = None

    if purchase.get("purchase_verified") or purchase.get("db_verified"):
        # Get business info from DB for category
        from app.database.models import get_business, get_order
        business_id = state.get("business_id", "")
        business = get_business(business_id) if business_id else None
        order = get_order(state.get("bill_id", ""))

        purchase_context = {
            "business_name": business["name"] if business else business_id,
            "business_category": business.get("category", "unknown") if business else "unknown",
            "items": order.get("items", []) if order else [],
            "amount": order.get("amount", 0) if order else 0,
            "order_date": order.get("order_date", "") if order else "",
        }
        print(f"   📦 Purchase context: {purchase_context['business_name']} ({purchase_context['business_category']}) — {purchase_context['items']}")

    result = run_consistency_agent(
        review_text=state.get("review_text", ""),
        purchase_context=purchase_context,
    )

    agents = state.get("agents_executed", []) + ["experience_consistency"]
    return {"consistency_result": result, "agents_executed": agents}


def duplicate_node(state: ReviewState) -> dict:
    """Node 4: Duplicate/Plagiarism Detection — check for copy-paste reviews."""
    print("\n🟣 ━━━ Node 4: Duplicate Detection Agent ━━━")

    if not state.get("run_duplicate", True):
        print("   ⏭️ Skipped (not required by intake)")
        return {
            "duplicate_result": {
                "is_duplicate": False,
                "similarity_score": 0.0,
                "matched_review_id": None,
                "flags": [],
            },
        }

    result = run_duplicate_agent(state.get("review_text", ""))

    agents = state.get("agents_executed", []) + ["duplicate_detection"]
    return {"duplicate_result": result, "agents_executed": agents}


def behavior_node(state: ReviewState) -> dict:
    """Node 5: Reviewer Behavior — analyze submission patterns."""
    print("\n🔵 ━━━ Node 5: Reviewer Behavior Agent ━━━")

    if not state.get("run_behavior", True):
        print("   ⏭️ Skipped (not required by intake)")
        return {
            "behavior_result": {
                "behavior_score": 0.85,
                "risk_level": "low",
                "review_count": 0,
                "flags": [],
            },
        }

    result = run_behavior_agent(bill_id=state.get("bill_id", ""))

    agents = state.get("agents_executed", []) + ["reviewer_behavior"]
    return {"behavior_result": result, "agents_executed": agents}


def media_auth_node(state: ReviewState) -> dict:
    """Node 6: Media Authenticity — analyze uploaded images with VISION."""
    print("\n🔴 ━━━ Node 6: Media Authenticity Agent ━━━")

    has_media = state.get("has_media", False)
    media_paths = state.get("media_paths", [])

    if not state.get("run_media_auth", False) and not media_paths:
        print("   ⏭️ Skipped (no media uploaded)")
        return {
            "media_auth_result": {
                "media_authentic": None,
                "authenticity_score": 0.0,
                "flags": [],
                "matches_review": None,
                "match_score": 0.0,
                "no_media": True,
            },
        }

    result = run_media_auth_agent(
        review_text=state.get("review_text", ""),
        has_media=has_media,
        media_paths=media_paths,
    )

    agents = state.get("agents_executed", []) + ["media_authenticity"]
    return {"media_auth_result": result, "agents_executed": agents}


def trust_score_node(state: ReviewState) -> dict:
    """Node 7: Trust Score — aggregate all signals into final verdict."""
    print("\n⭐ ━━━ Node 7: Trust Score Agent ━━━")

    purchase = state.get("purchase_result", {})
    consistency = state.get("consistency_result", {})
    duplicate = state.get("duplicate_result", {})
    behavior = state.get("behavior_result", {})
    media_auth = state.get("media_auth_result", {})

    has_media = state.get("has_media", False) and not media_auth.get("no_media", False)

    trust_input = {
        "purchase_verified": purchase.get("purchase_verified", False),
        "purchase_confidence": purchase.get("confidence", 0.0),
        "consistency_score": consistency.get("consistency_score", 0.5),
        "consistency_issues": consistency.get("issues_found", []),
        "is_duplicate": duplicate.get("is_duplicate", False),
        "similarity_score": duplicate.get("similarity_score", 0.0),
        "duplicate_flags": duplicate.get("flags", []),
        "behavior_score": behavior.get("behavior_score", 0.85),
        "behavior_risk_level": behavior.get("risk_level", "low"),
        "behavior_flags": behavior.get("flags", []),
        "has_media": has_media,
        "media_authentic": media_auth.get("media_authentic", None),
        "media_authenticity_score": media_auth.get("authenticity_score", 0.0),
        "media_matches_review": media_auth.get("matches_review", None),
        "media_match_score": media_auth.get("match_score", 0.0),
    }

    result = run_trust_score_agent(trust_input)

    agents = state.get("agents_executed", []) + ["trust_score"]
    return {"trust_result": result, "agents_executed": agents}


def save_review_node(state: ReviewState) -> dict:
    """Node 8: Save Review — persist the review and results to the database."""
    print("\n💾 ━━━ Node 8: Saving Review to Database ━━━")

    trust = state.get("trust_result", {})

    try:
        review_id = save_review(
            order_id=state.get("bill_id", ""),
            business_id=state.get("business_id", ""),
            review_text=state.get("review_text", ""),
            trust_score=trust.get("final_trust_score", 0),
            trust_level=trust.get("trust_level", "Medium"),
            action=trust.get("action", "review"),
            breakdown=trust.get("breakdown", {}),
            agents_log={
                "agents_executed": state.get("agents_executed", []),
                "intake": state.get("intake_result", {}),
                "purchase": state.get("purchase_result", {}),
                "consistency": state.get("consistency_result", {}),
                "duplicate": state.get("duplicate_result", {}),
                "behavior": state.get("behavior_result", {}),
                "media_auth": state.get("media_auth_result", {}),
            },
            has_media=state.get("has_media", False),
        )

        # Save media metadata if images were uploaded
        media_paths = state.get("media_paths", [])
        media_auth = state.get("media_auth_result", {})
        per_image = media_auth.get("per_image_results", [])

        for i, path in enumerate(media_paths):
            image_result = per_image[i] if i < len(per_image) else {}
            save_review_media(
                review_id=review_id,
                file_path=path,
                file_type="image",
                original_name=path.split("/")[-1],
                vision_analysis=image_result,
                matches_review=image_result.get("matches_review", True),
                match_score=image_result.get("match_score", 0.5),
            )

        print(f"   ✅ Review saved with ID: {review_id}")
        return {"review_id": review_id}

    except Exception as e:
        print(f"   ❌ Failed to save review: {e}")
        traceback.print_exc()
        return {"review_id": None}


# ══════════════════════════════════════════════════════════════
# BUILD THE GRAPH
# ══════════════════════════════════════════════════════════════

def build_review_graph() -> StateGraph:
    """Build the LangGraph StateGraph with 8 nodes (7 agents + save)."""

    graph = StateGraph(ReviewState)

    graph.add_node("intake", intake_node)
    graph.add_node("purchase", purchase_node)
    graph.add_node("consistency", consistency_node)
    graph.add_node("duplicate", duplicate_node)
    graph.add_node("behavior", behavior_node)
    graph.add_node("media_auth", media_auth_node)
    graph.add_node("trust_score", trust_score_node)
    graph.add_node("save_review", save_review_node)

    graph.set_entry_point("intake")

    graph.add_edge("intake", "purchase")
    graph.add_edge("purchase", "consistency")
    graph.add_edge("consistency", "duplicate")
    graph.add_edge("duplicate", "behavior")
    graph.add_edge("behavior", "media_auth")
    graph.add_edge("media_auth", "trust_score")
    graph.add_edge("trust_score", "save_review")
    graph.add_edge("save_review", END)

    return graph.compile()


_compiled_graph = None


def get_review_graph():
    """Get the compiled review graph (lazy singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        print("🔧 Building LangGraph review pipeline...")
        _compiled_graph = build_review_graph()
        print("✅ LangGraph review pipeline ready!")
    return _compiled_graph


def run_review_pipeline(input_data: dict) -> dict:
    """Run the full review verification pipeline."""
    graph = get_review_graph()

    initial_state = {
        "business_id": input_data.get("business_id", ""),
        "bill_id": input_data.get("bill_id", ""),
        "review_text": input_data.get("review_text", ""),
        "has_media": input_data.get("has_media", False),
        "media_paths": input_data.get("media_paths", []),
        "agents_executed": [],
    }

    print("\n" + "=" * 60)
    print("🚀 STARTING REVIEW VERIFICATION PIPELINE (7 Agents)")
    print(f"   Business: {initial_state['business_id']}")
    print(f"   Bill: {initial_state['bill_id']}")
    print(f"   Review: {initial_state['review_text'][:80]}...")
    print(f"   Has Media: {initial_state['has_media']}")
    print(f"   Media Files: {len(initial_state['media_paths'])}")
    print("=" * 60)

    try:
        final_state = graph.invoke(initial_state)

        trust_result = final_state.get("trust_result", {})
        agents = final_state.get("agents_executed", [])
        review_id = final_state.get("review_id")

        print("\n" + "=" * 60)
        print("🏁 PIPELINE COMPLETE")
        print(f"   Agents executed: {agents}")
        print(f"   Trust Score: {trust_result.get('final_trust_score', 'N/A')}")
        print(f"   Trust Level: {trust_result.get('trust_level', 'N/A')}")
        print(f"   Action: {trust_result.get('action', 'N/A')}")
        print(f"   Review ID: {review_id}")
        print("=" * 60 + "\n")

        trust_result["agents_executed"] = agents
        trust_result["pipeline"] = "langgraph"
        trust_result["review_id"] = review_id

        # Include media analysis in response
        media_auth = final_state.get("media_auth_result", {})
        if media_auth.get("image_description"):
            trust_result["media_analysis"] = {
                "image_description": media_auth.get("image_description", ""),
                "matches_review": media_auth.get("matches_review", True),
                "match_score": media_auth.get("match_score", 1.0),
                "match_explanation": media_auth.get("match_explanation", ""),
            }

        # Include purchase details
        purchase = final_state.get("purchase_result", {})
        if purchase.get("order_details"):
            trust_result["order_details"] = purchase["order_details"]
        trust_result["db_verified"] = purchase.get("db_verified", False)

        return trust_result

    except Exception as e:
        print(f"\n❌ PIPELINE ERROR: {e}")
        traceback.print_exc()
        return {
            "final_trust_score": 50,
            "trust_level": "Medium",
            "breakdown": {
                "purchase_points": 0,
                "consistency_points": 10,
                "duplicate_points": 10,
                "behavior_points": 10,
                "media_points": 0,
            },
            "recommendation": "Pipeline error — manual review recommended",
            "action": "review",
            "error": str(e),
            "pipeline": "langgraph_fallback",
        }
