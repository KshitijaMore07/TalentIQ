# TalentIQ - AI-Powered Recruitment & Interview Management Platform

**Intelligent Recruitment. Smarter Hiring.**

Parse resumes with Gemini, find candidates with semantic search, rank them with an explainable hybrid score and manage interviews end to end. Three portals: **Candidate**, **Admin recruitment** and **Interviewer**.

**Stack:** React + Vite | Flask + Flask-SQLAlchemy | MySQL | Google Gemini | Sentence Transformers | ChromaDB | PyMuPDF, python-docx | JWT

## Quick start
Prerequisites: Python 3.11+, Node.js 18+, MySQL 8 (or set `USE_SQLITE=true` for a zero-setup demo), Git.

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env  -> then edit values
python run.py                    # http://localhost:5000  (creates DB, tables and demo data)

# Frontend (new terminal)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```
The first run downloads the Sentence Transformers model (about 90 MB). Without `GEMINI_API_KEY` a basic rule-based parser is used so the app still works; add a key for full AI parsing.

**Demo logins:** recruiter `admin@talentiq.com` / `Admin@123`, interviewer `interviewer@talentiq.com` / `Interview@123`. Candidates register themselves.

**Sample data:** `python backend/scripts/make_sample_resumes.py` creates 5 fictional DOCX resumes in `sample_data/resumes/` for bulk upload.

## Features
- Candidate portal: register, upload resume (PDF/DOCX), review/correct extracted data, apply, track status, see interviews.
- Bulk resume upload with per-file status (Completed/Failed/Processing), duplicate detection by email, invalid files isolated.
- Jobs CRUD, dashboard, candidate search/filter, internal notes, correction of AI output.
- Hybrid matching (0-100) with matched/missing skills and explanation; natural-language semantic search.
- Shortlisting per job, CSV export, approval notifications, interview scheduling/rescheduling/cancelling, interviewer feedback.
- Security: JWT, password hashing, role-based access, upload type/size validation, candidates cannot read other profiles.

## Scoring
Required skills 40% | Experience 20% | Education 10% | Preferred skills 10% | Semantic similarity 20%. Calculated in code, never by the LLM. Details in `docs/matching-methodology.md`.

## API overview
Auth `/api/auth/register|login` | Candidate `/api/candidates/profile`, `/api/resumes/upload` | Admin `/api/resumes/bulk-upload`, `/api/jobs`, `/api/matching/{job_id}`, `/api/search`, `/api/shortlists`, `/api/interviews`, `/api/interviews/{id}/feedback`.

## Test scenarios
1 Candidate uploads resume | 2 Admin uploads 5 resumes | 3 Invalid file is handled without stopping others | 4 Create job | 5 Match job -> ranked scores | 6 Natural language search | 7 View profile + explanation | 8 Shortlist | 9 Approve -> notification | 10 Schedule interview | 11 Interviewer feedback | 12 Candidate opening another profile -> 403 Access denied.

## Notes
- If you switch between hashing fallback and real embeddings, call `POST /api/admin/reindex` (or delete `backend/chroma_data`).
- Email needs the optional `SMTP_*` values; notifications always appear in the app.
- The brand name is set in `frontend/src/api.js` (`BRAND`) and the page title in `frontend/index.html`.

**Author:** Kshitija Sunil More | [KshitijaMore07](https://github.com/KshitijaMore07) | AI Intern technical assessment
