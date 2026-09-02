from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/rankings")
def get_rankings(db: Session = Depends(get_db)):
    # Latest score per user, joined with basic profile info
    subq = (
        db.query(
            models.ReadinessScore.user_id,
            func.max(models.ReadinessScore.computed_at).label("latest"),
        )
        .group_by(models.ReadinessScore.user_id)
        .subquery()
    )

    results = (
        db.query(models.User.full_name, models.User.email, models.ReadinessScore.score)
        .join(models.ReadinessScore, models.ReadinessScore.user_id == models.User.id)
        .join(
            subq,
            (models.ReadinessScore.user_id == subq.c.user_id)
            & (models.ReadinessScore.computed_at == subq.c.latest),
        )
        .order_by(models.ReadinessScore.score.desc())
        .all()
    )

    return [
        {"name": r.full_name, "email": r.email, "score": round(r.score, 2)}
        for r in results
    ]
