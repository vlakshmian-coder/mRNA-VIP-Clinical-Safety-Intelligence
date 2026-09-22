"""Neon PostgreSQL persistence for the mRNA-VIP pipeline.

Neon is used for application metadata and generated-report persistence.
ChromaDB remains the project's RAG vector store.

Set DATABASE_URL in the environment (or a local .env file) before connecting.
Never commit real credentials or connection strings.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.types import JSON
from dotenv import load_dotenv

load_dotenv()
class Base(DeclarativeBase):
    """Base class for Neon persistence models."""


JsonType = JSON().with_variant(JSONB(), "postgresql")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    patient_id: Mapped[str] = mapped_column(String(128), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_band: Mapped[str | None] = mapped_column(String(64), nullable=True)
    report_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    k: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False)


class ClinicalReport(Base):
    __tablename__ = "clinical_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    report_json: Mapped[dict[str, Any]] = mapped_column(JsonType, nullable=False)


def get_database_url() -> str:
    """Return DATABASE_URL or raise a clear configuration error."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add the Neon PostgreSQL connection string "
            "to your environment; never commit it to the repository."
        )
    return url


def get_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine for Neon/PostgreSQL."""
    url = database_url or get_database_url()
    return create_engine(url, pool_pre_ping=True)


def init_db(database_url: str | None = None) -> None:
    """Create the mRNA-VIP persistence tables if they do not exist."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)


def create_pipeline_run(
    run_id: str,
    patient_id: str,
    model_name: str | None = None,
    risk_score: float | None = None,
    risk_band: str | None = None,
    report_status: str = "pending",
    database_url: str | None = None,
) -> None:
    """Persist one pipeline execution record."""
    engine = get_engine(database_url)
    Session = sessionmaker(bind=engine)
    with Session.begin() as session:
        session.add(
            PipelineRun(
                run_id=run_id,
                patient_id=patient_id,
                model_name=model_name,
                risk_score=risk_score,
                risk_band=risk_band,
                report_status=report_status,
            )
        )


def log_retrieval(
    run_id: str,
    question: str,
    k: int,
    latency_seconds: float,
    chunk_count: int,
    database_url: str | None = None,
) -> None:
    """Persist one ChromaDB retrieval event."""
    engine = get_engine(database_url)
    Session = sessionmaker(bind=engine)
    with Session.begin() as session:
        session.add(
            RetrievalLog(
                run_id=run_id,
                question=question,
                k=k,
                latency_seconds=latency_seconds,
                chunk_count=chunk_count,
            )
        )


def save_clinical_report(
    run_id: str,
    report: dict[str, Any],
    database_url: str | None = None,
) -> None:
    """Persist a validated ClinicalSafetyReport payload."""
    engine = get_engine(database_url)
    Session = sessionmaker(bind=engine)
    with Session.begin() as session:
        session.add(
            ClinicalReport(
                run_id=run_id,
                report_json=json.loads(json.dumps(report)),
            )
        )


if __name__ == "__main__":
    init_db()
    print("mRNA-VIP Neon tables initialized successfully.")
