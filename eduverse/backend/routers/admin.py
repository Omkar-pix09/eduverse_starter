import os
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db
from deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")


@router.post("/dataset/upload")
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """Admin uploads a CSV of 100-3k student records for bulk ML training/analysis.
    Expected columns (case-insensitive, extras are kept in raw_row):
    cgpa, internships, projects_count, certifications_count,
    dsa_problems_solved, communication_score, placed
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    df = pd.read_csv(save_path)
    df.columns = [c.strip().lower() for c in df.columns]

    inserted = 0
    for _, row in df.iterrows():
        record = models.DatasetRecord(
            source_batch=file.filename,
            cgpa=row.get("cgpa"),
            internships=row.get("internships"),
            projects_count=row.get("projects_count"),
            certifications_count=row.get("certifications_count"),
            dsa_problems_solved=row.get("dsa_problems_solved"),
            communication_score=row.get("communication_score"),
            placed=row.get("placed"),
            raw_row=row.to_dict(),
        )
        db.add(record)
        inserted += 1

    db.commit()
    return {"filename": file.filename, "rows_imported": inserted}


@router.get("/dataset/summary")
def dataset_summary(
    db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    total = db.query(models.DatasetRecord).count()
    placed = db.query(models.DatasetRecord).filter(models.DatasetRecord.placed == 1).count()
    return {"total_records": total, "placed_count": placed, "placement_rate": (placed / total * 100) if total else 0}


@router.get("/users")
def list_users(db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    return db.query(models.User).all()
