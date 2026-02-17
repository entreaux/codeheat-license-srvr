import json
import secrets
import stripe
from fastapi import APIRouter, Request, HTTPException
from .config import settings
from .db import SessionLocal
from .models import LicenseRecord
from .minter_loader import load_mint_function

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

def infer_tier_from_price_id(price_id: str) -> str:
    if price_id == settings.PRICE_STANDARD:
        return "standard"
    if price_id == settings.PRICE_COMMERCIAL:
        return "commercial"
    return ""

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    if event["type"] != "checkout.session.completed":
        return {"ok": True}

    session = event["data"]["object"]
    session_id = session["id"]

    # Only mint if paid
    if session.get("payment_status") != "paid":
        return {"ok": True, "ignored": "payment_status_not_paid"}

    # Fetch full session with line_items (for robust tier inference)
    full = stripe.checkout.Session.retrieve(
        session_id,
        expand=["line_items.data.price", "customer"]
    )

    email = None
    cd = full.get("customer_details") or {}
    email = cd.get("email") or full.get("customer_email")
    if not email:
        raise HTTPException(status_code=400, detail="Missing customer email")

    tier = (full.get("metadata") or {}).get("tier", "").strip().lower()

    if tier not in ("standard", "commercial"):
        # fallback: infer tier from price id
        items = (full.get("line_items") or {}).get("data", [])
        if not items:
            raise HTTPException(status_code=400, detail="No line_items to infer tier")
        price_id = items[0]["price"]["id"]
        tier = infer_tier_from_price_id(price_id)
        if tier not in ("standard", "commercial"):
            raise HTTPException(status_code=400, detail=f"Unknown price id: {price_id}")

    db = SessionLocal()
    try:
        existing = db.query(LicenseRecord).filter(LicenseRecord.session_id == session_id).first()
        if existing:
            return {"ok": True, "idempotent": True}

        # deterministic-ish license id (no global counter required)
        license_id = f"CH-2026-{session_id[-10:]}"

        mint_license = load_mint_function()
        license_obj = mint_license(
            email=email,
            tier=tier,
            license_id=license_id,
            session_id=session_id
        )

        if not isinstance(license_obj, dict) or "payload" not in license_obj or "signature" not in license_obj:
            raise RuntimeError("Minter must return dict with keys: payload, signature")

        # store compact json
        license_json = json.dumps(license_obj, separators=(",", ":"))

        token = secrets.token_urlsafe(32)

        rec = LicenseRecord(
            session_id=session_id,
            email=email,
            tier=tier,
            download_token=token,
            license_json=license_json
        )
        db.add(rec)
        db.commit()

    finally:
        db.close()

    return {"ok": True}
