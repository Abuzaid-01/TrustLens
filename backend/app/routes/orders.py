"""
Orders API — Order lookup and validation endpoints.
"""

from fastapi import APIRouter
from app.database.models import lookup_order, get_all_businesses, get_orders_by_business

router = APIRouter()


@router.get("/orders/lookup")
async def order_lookup(order_id: str):
    """
    Look up an order by ID. Used by the frontend to validate
    the order before submitting a review.
    """
    return lookup_order(order_id)


@router.get("/businesses")
async def list_businesses():
    """List all registered businesses."""
    return get_all_businesses()


@router.get("/orders/{business_id}")
async def list_orders(business_id: str):
    """List orders for a specific business."""
    orders = get_orders_by_business(business_id)
    return {"business_id": business_id, "orders": orders, "count": len(orders)}
