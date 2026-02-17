from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from .db import SessionLocal
from .models import LicenseRecord

router = APIRouter()

@router.get("/download/{token}")
def download_license(token: str):
    db = SessionLocal()
    try:
        rec = db.query(LicenseRecord).filter(LicenseRecord.download_token == token).first()
        if not rec:
            raise HTTPException(status_code=404, detail="Invalid token")

        # Optional one-time download:
        # if rec.downloaded:
        #     raise HTTPException(status_code=410, detail="Link already used")
        # rec.downloaded = True
        # db.commit()

        filename = f"CodeHeat-{rec.tier}-{rec.session_id[-8:]}.license"
        return Response(
            content=rec.license_json.encode("utf-8"),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    finally:
        db.close()
