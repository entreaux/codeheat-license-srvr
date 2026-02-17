import os

def must(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

class Settings:
    STRIPE_SECRET_KEY = must("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = must("STRIPE_WEBHOOK_SECRET")

    PRICE_STANDARD = must("PRICE_STANDARD")
    PRICE_COMMERCIAL = must("PRICE_COMMERCIAL")

    PUBLIC_BASE_URL = must("PUBLIC_BASE_URL").rstrip("/")

    DATABASE_URL = must("DATABASE_URL")

    # Private key (base64) – never commit
    LICENSE_PRIVATE_KEY_B64 = must("LICENSE_PRIVATE_KEY_B64")

    # Private minter python module (base64) – never commit
    # For local dev, you can use private/license_minter.py instead.
    LICENSE_MINTER_PY_B64 = os.environ.get("LICENSE_MINTER_PY_B64", "").strip()

settings = Settings()
