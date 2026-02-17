import datetime as dt
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Boolean
from .db import Base

class LicenseRecord(Base):
    __tablename__ = "licenses"

    # Stripe checkout session id
    session_id: Mapped[str] = mapped_column(String(128), primary_key=True)

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    tier: Mapped[str] = mapped_column(String(32), nullable=False)

    # unguessable download token
    download_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    # stored license json: {"payload":"...","signature":"..."}
    license_json: Mapped[str] = mapped_column(Text, nullable=False)

    downloaded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, nullable=False)
