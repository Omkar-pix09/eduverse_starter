# EduVerse — Backend Starter (Day 1 Scaffold)

AI-powered placement readiness platform with dual data paths (bulk dataset + manual
profiles), user/admin roles, ML readiness scoring, AI career assistant, and a
resume builder with ATS scoring.

## What's already built
| Module | Endpoint prefix | Status |
|---|---|---|
| Auth (register/login, JWT) | `/api/auth` | ✅ working |
| Profile (manual entry + GitHub sync) | `/api/profile` | ✅ working |
| ML Analytics (readiness score) | `/api/analytics` | ⚠️ needs trained model (see below) |
| AI Career Assistant (Gemini) | `/api/chatbot` | ⚠️ needs `GEMINI_API_KEY` |
| Recruiter/TPO Dashboard | `/api/dashboard` | ✅ working |
| **Admin: dataset upload (100-3k rows)** | `/api/admin` | ✅ working |
| **Resume Builder + ATS Checker** | `/api/resume` | ✅ working |

## Two data paths (your key differentiator)
1. **Bulk path**: Admin uploads a CSV (`/api/admin/dataset/upload`) → rows land in
   `dataset_records` table → used to train the ML model.
2. **Manual path**: Any student registers, fills their own profile
   (`/api/profile`), connects GitHub, builds a resume — completely independent
   of the bulk dataset, but scored by the *same* trained model.

## Setup (do this first)
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in real values
```

Fill `.env`:
- `DATABASE_URL` — from Supabase (Project Settings → Database → Connection String)
- `SECRET_KEY` — any long random string
- `GEMINI_API_KEY` — from Google AI Studio

## Run it
```bash
uvicorn main:app --reload
```
Visit `http://localhost:8000/docs` — FastAPI auto-generates a full interactive
API tester. Use this to try every endpoint before building any frontend screen.

## Making a user an admin
There's no signup flow for admin yet (by design — admins shouldn't self-register).
After registering normally, manually set `role = 'admin'` for that user directly
in the database (Supabase table editor) for now.

## Train the ML model (needed before /api/analytics/predict works)
1. Put your dataset CSV in `ml/` (or use the one uploaded via `/api/admin/dataset/upload`)
2. Write `ml/train_model.py`:
   - Load data (from CSV or query `dataset_records` table)
   - Features: `cgpa, projects_count/skills_count, repo_count, total_stars` (match `routers/analytics.py`)
   - Train `RandomForestClassifier` or `XGBClassifier`
   - `joblib.dump(model, "readiness_model.pkl")`
3. Copy the `.pkl` into `backend/ml_models/readiness_model.pkl`

## Next steps (in order)
1. Run this backend locally, test every endpoint in `/docs`
2. Write `ml/train_model.py`, get a real trained model in place
3. Scaffold the React frontend (Vite + TS + Tailwind) — login, profile form, dashboard
4. Build the Admin UI (CSV upload button, dataset summary view)
5. Build the Resume Builder UI (form + "Download Resume" + ATS score display)
6. Deploy: Vercel (frontend) + Render (backend) + Supabase (DB)
