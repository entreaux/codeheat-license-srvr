from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
from .config import settings

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutReq(BaseModel):
    tier: str  # "standard" | "commercial"

def _price_for_tier(tier: str) -> str:
    t = tier.lower().strip()
    if t == "standard":
        return settings.PRICE_STANDARD
    if t == "commercial":
        return settings.PRICE_COMMERCIAL
    raise ValueError("tier must be: standard | commercial")

@router.post("/api/checkout")
def create_checkout(req: CheckoutReq):
    try:
        price_id = _price_for_tier(req.tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        # store tier in metadata (nice), but webhook also infers from price_id as fallback
        metadata={"tier": req.tier.lower().strip()},
        success_url=f"{settings.PUBLIC_BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.PUBLIC_BASE_URL}/cancel"
    )
    return {"url": session.url}
