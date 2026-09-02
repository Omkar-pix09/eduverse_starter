from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # noqa: F401 - ensures models are registered before create_all
from routers import auth, profile, analytics, chatbot, dashboard, admin, resume

# Creates all tables that don't exist yet - safe to run every startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduVerse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your Vercel URL before final submission
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(analytics.router)
app.include_router(chatbot.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(resume.router)


@app.get("/")
def health_check():
    return {"status": "EduVerse API is running"}
