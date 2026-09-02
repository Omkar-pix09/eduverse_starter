import os
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


@router.post("/{user_id}/ask")
def ask(user_id: int, req: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Set GEMINI_API_KEY in .env")

    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    system_context = (
        f"You are EduVerse's AI career assistant. Student profile: "
        f"CGPA={profile.cgpa if profile else 'unknown'}, "
        f"Skills={profile.skills if profile else []}. "
        f"Answer career and placement questions concisely and practically."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{system_context}\n\nStudent question: {req.message}")
    answer = response.text

    db.add(models.ChatHistory(user_id=user_id, message=req.message, response=answer))
    db.commit()

    return {"response": answer}
