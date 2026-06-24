"""Read API for opportunities with the filters from SPEC §10."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Opportunity
from app.schemas import OpportunityListOut, OpportunityOut

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=OpportunityListOut)
def list_opportunities(
    session: Session = Depends(get_session),
    source_type: list[str] | None = Query(default=None),
    buyer_type: list[str] | None = Query(default=None),
    min_score: float = Query(default=0.0, ge=0, le=100),
    deadline_within_days: int | None = Query(default=None, ge=0),
    tags: list[str] | None = Query(default=None),
    country: str | None = Query(default=None),
    q: str | None = Query(default=None, description="search in title/summary"),
    sort: str = Query(default="-relevance_score"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    conditions = [Opportunity.relevance_score >= min_score]

    if source_type:
        conditions.append(Opportunity.source_type.in_(source_type))
    if buyer_type:
        conditions.append(Opportunity.buyer_type.in_(buyer_type))
    if country:
        conditions.append(Opportunity.country.ilike(f"%{country}%"))
    if tags:
        conditions.append(Opportunity.tags.overlap(tags))
    if deadline_within_days is not None:
        cutoff = date.today() + timedelta(days=deadline_within_days)
        conditions.append(Opportunity.deadline.is_not(None))
        conditions.append(Opportunity.deadline <= cutoff)
        conditions.append(Opportunity.deadline >= date.today())
    if q:
        like = f"%{q}%"
        conditions.append(
            Opportunity.title.ilike(like) | Opportunity.summary.ilike(like)
        )

    sort_columns = {
        "relevance_score": Opportunity.relevance_score,
        "design_fit_score": Opportunity.design_fit_score,
        "deadline": Opportunity.deadline,
        "posted_date": Opportunity.posted_date,
        "created_at": Opportunity.created_at,
    }
    desc = sort.startswith("-")
    key = sort[1:] if desc else sort
    col = sort_columns.get(key, Opportunity.relevance_score)
    order = col.desc() if desc else col.asc()

    total = session.scalar(
        select(func.count()).select_from(Opportunity).where(*conditions)
    )
    rows = session.scalars(
        select(Opportunity).where(*conditions).order_by(order).limit(limit).offset(offset)
    ).all()

    return OpportunityListOut(
        total=total or 0,
        limit=limit,
        offset=offset,
        items=[OpportunityOut.model_validate(_serialize(r)) for r in rows],
    )


@router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, session: Session = Depends(get_session)):
    opp = session.get(Opportunity, opportunity_id)
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return OpportunityOut.model_validate(_serialize(opp))


def _serialize(opp: Opportunity) -> dict:
    data = {c.name: getattr(opp, c.name) for c in Opportunity.__table__.columns}
    data["id"] = str(opp.id)
    data["budget_min"] = float(opp.budget_min) if opp.budget_min is not None else None
    data["budget_max"] = float(opp.budget_max) if opp.budget_max is not None else None
    return data
