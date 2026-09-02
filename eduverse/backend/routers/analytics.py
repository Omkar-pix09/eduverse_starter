import os
import joblib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "readiness_model.pkl")
_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(
                status_code=503,
                detail="Model not trained yet. Run ml/train_model.py first and copy the .pkl here.",
            )
        _model = joblib.load(MODEL_PATH)
    return _model


@router.post("/predict/{user_id}")
def predict_readiness(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    github = (
        db.query(models.GitHubData)
        .filter(models.GitHubData.user_id == user_id)
        .order_by(models.GitHubData.synced_at.desc())
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    model = get_model()

    # Feature vector must match training feature order in ml/train_model.py
    features = [[
        profile.cgpa or 0,
        len(profile.skills or []),
        github.repo_count if github else 0,
        github.total_stars if github else 0,
    ]]

    score = float(model.predict_proba(features)[0][1]) * 100  # probability of "placement-ready"

    record = models.ReadinessScore(user_id=user_id, score=score)
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"user_id": user_id, "readiness_score": round(score, 2)}
