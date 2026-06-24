"""Read + write API for opportunities (filters from SPEC §10, dashboard actions)."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Opportunity, OpportunityStatus, PipelineStatus
from app.schemas import (
    Facets,
    OpportunityListOut,
    OpportunityOut,
    OpportunityUpdate,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=OpportunityListOut)
def list_opportunities(
    session: Session = Depends(get_session),
    source_type: list[str] | None = Query(default=None),
    buyer_type: list[str] | None = Query(default=None),
    pipeline_status: list[str] | None = Query(default=None),
    saved: bool | None = Query(default=None),
    min_score: float = Query(default=0.0, ge=0, le=100),
    deadline_within_days: int | None = Query(default=None, ge=0),
    tags: list[str] | None = Query(default=None),
    country: str | None = Query(default=None),
    q: str | None = Query(default=None, description="search in title/summary"),
    sort: str = Query(default="-relevance_score"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    conditions = [Opportunity.relevance_score >= min_score]

    if source_type:
        conditions.append(Opportunity.source_type.in_(source_type))
    if buyer_type:
        conditions.append(Opportunity.buyer_type.in_(buyer_type))
    if saved is not None:
        conditions.append(Opportunity.saved.is_(saved))
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
    if pipeline_status:
        conditions.append(OpportunityStatus.status.in_(pipeline_status))

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

    base = (
        select(Opportunity, OpportunityStatus)
        .outerjoin(OpportunityStatus, OpportunityStatus.opportunity_id == Opportunity.id)
        .where(*conditions)
    )
    count_stmt = (
        select(func.count())
        .select_from(Opportunity)
        .outerjoin(OpportunityStatus, OpportunityStatus.opportunity_id == Opportunity.id)
        .where(*conditions)
    )
    total = session.scalar(count_stmt)
    rows = session.execute(
        base.order_by(order).limit(limit).offset(offset)
    ).all()

    return OpportunityListOut(
        total=total or 0,
        limit=limit,
        offset=offset,
        items=[OpportunityOut.model_validate(_serialize(opp, st)) for opp, st in rows],
    )


@router.get("/facets", response_model=Facets)
def facets(session: Session = Depends(get_session)):
    def distinct(col):
        return [
            v for (v,) in session.execute(select(col).distinct().where(col.is_not(None)))
            if v
        ]

    # tags is an array column — unnest it
    tag_rows = session.execute(
        select(func.unnest(Opportunity.tags)).distinct()
    ).all()
    tags = sorted({t for (t,) in tag_rows if t})

    return Facets(
        source_types=sorted(distinct(Opportunity.source_type)),
        buyer_types=sorted(distinct(Opportunity.buyer_type)),
        tags=tags,
        countries=sorted(distinct(Opportunity.country)),
        pipeline_statuses=[s.value for s in PipelineStatus],
    )


@router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, session: Session = Depends(get_session)):
    row = session.execute(
        select(Opportunity, OpportunityStatus)
        .outerjoin(OpportunityStatus, OpportunityStatus.opportunity_id == Opportunity.id)
        .where(Opportunity.id == opportunity_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opp, st = row
    return OpportunityOut.model_validate(_serialize(opp, st))


@router.patch("/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    session: Session = Depends(get_session),
):
    opp = session.get(Opportunity, opportunity_id)
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if payload.saved is not None:
        opp.saved = payload.saved

    status_row = session.scalar(
        select(OpportunityStatus).where(
            OpportunityStatus.opportunity_id == opp.id
        )
    )
    if status_row is None:
        status_row = OpportunityStatus(
            opportunity_id=opp.id, status=PipelineStatus.new.value
        )
        session.add(status_row)

    if payload.pipeline_status is not None:
        valid = {s.value for s in PipelineStatus}
        if payload.pipeline_status not in valid:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status. Must be one of {sorted(valid)}",
            )
        status_row.status = payload.pipeline_status
    if payload.notes is not None:
        status_row.notes = payload.notes

    status_row.updated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(opp)
    session.refresh(status_row)
    return OpportunityOut.model_validate(_serialize(opp, status_row))


def _serialize(opp: Opportunity, status_row: OpportunityStatus | None) -> dict:
    data = {c.name: getattr(opp, c.name) for c in Opportunity.__table__.columns}
    data["id"] = str(opp.id)
    data["budget_min"] = float(opp.budget_min) if opp.budget_min is not None else None
    data["budget_max"] = float(opp.budget_max) if opp.budget_max is not None else None
    data["pipeline_status"] = (
        status_row.status if status_row else PipelineStatus.new.value
    )
    data["notes"] = status_row.notes if status_row else None
    return data
