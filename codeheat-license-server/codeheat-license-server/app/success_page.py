from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .config import settings
from .db import SessionLocal
from .models import LicenseRecord

router = APIRouter()

@router.get("/api/license-status")
def license_status(session_id: str):
    db = SessionLocal()
    try:
        rec = db.query(LicenseRecord).filter(LicenseRecord.session_id == session_id).first()
        if not rec:
            return {"ready": False}
        return {
            "ready": True,
            "download_url": f"{settings.PUBLIC_BASE_URL}/download/{rec.download_token}"
        }
    finally:
        db.close()

@router.get("/success", response_class=HTMLResponse)
def success(session_id: str):
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>License</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 40px; }}
    .box {{ max-width: 760px; padding: 24px; border: 1px solid #ddd; border-radius: 12px; }}
    code {{ background: #f6f6f6; padding: 2px 6px; border-radius: 6px; }}
    a.btn {{ display:inline-block; padding:10px 14px; border:1px solid #111; border-radius:10px; text-decoration:none; }}
  </style>
</head>
<body>
  <div class="box">
    <h2>Payment received</h2>
    <p>Session: <code>{session_id}</code></p>
    <p id="status">Waiting for license minting…</p>
    <p id="link"></p>
  </div>

<script>
async function poll() {{
  const r = await fetch("/api/license-status?session_id={session_id}");
  const j = await r.json();
  if (!j.ready) {{
    document.getElementById("status").innerText = "Minting… (Stripe webhook processing)";
    setTimeout(poll, 1200);
    return;
  }}
  document.getElementById("status").innerText = "License ready:";
  document.getElementById("link").innerHTML = `<a class="btn" href="${{j.download_url}}">Download license</a>`;
}}
poll();
</script>
</body>
</html>
"""
    return HTMLResponse(html)

@router.get("/cancel", response_class=HTMLResponse)
def cancel():
    return HTMLResponse("<h2>Payment cancelled</h2>")
