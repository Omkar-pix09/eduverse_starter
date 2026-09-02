import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.put("/{user_id}")
def update_profile(user_id: int, data: schemas.ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/{user_id}/sync-github")
def sync_github(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile or not profile.github_username:
        raise HTTPException(status_code=400, detail="Set github_username on profile first")

    username = profile.github_username
    resp = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="GitHub user not found or rate-limited")

    repos = resp.json()
    languages = {}
    top_repos = []
    total_stars = 0

    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
        stars = repo.get("stargazers_count", 0)
        total_stars += stars
        top_repos.append({"name": repo["name"], "stars": stars, "language": lang})

    top_repos = sorted(top_repos, key=lambda r: r["stars"], reverse=True)[:5]

    github_data = models.GitHubData(
        user_id=user_id,
        repo_count=len(repos),
        total_stars=total_stars,
        languages=languages,
        top_repos=top_repos,
    )
    db.add(github_data)
    db.commit()
    db.refresh(github_data)
    return github_data
