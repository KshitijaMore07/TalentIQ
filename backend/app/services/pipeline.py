import os, json
from uuid import uuid4
from werkzeug.utils import secure_filename
from config import Config
from ..extensions import db
from ..models import Candidate, CandidateSkill, Resume
from .parser import extract_text, parse_resume
from .embeddings import index_candidate


def clean_list(v):
    if isinstance(v, str):
        v = v.split(",")
    seen, out = set(), []
    for s in v or []:
        s = str(s).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower()); out.append(s)
    return out


def apply_data(c, d, keep_identity=False):
    for k in ("name", "phone", "location", "summary"):
        if k in d and d[k] is not None and not (keep_identity and k == "name" and c.name):
            setattr(c, k, d[k])
    if not keep_identity and d.get("email"):
        c.email = d["email"]
    if "experience_years" in d:
        c.experience_years = float(d["experience_years"] or 0)
    for k in ("education", "experience", "projects"):
        if k in d and isinstance(d[k], list):
            setattr(c, k, json.dumps(d[k]))
    if "skills" in d:
        c.skills = [CandidateSkill(skill=s) for s in clean_list(d["skills"])]


def save_upload(f):
    name = secure_filename(f.filename or "")
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ("pdf", "docx"):
        raise ValueError("Only PDF and DOCX files are allowed")
    path = os.path.join(Config.UPLOAD_DIR, "resumes", f"{uuid4().hex}.{ext}")
    f.save(path)
    return name, path


def process_resume(f, owner=None):
    """Upload -> text -> Gemini parse -> MySQL -> embedding. Each file is isolated so one failure never stops a batch."""
    res = Resume(filename=f.filename or "unknown", status="Processing", candidate_id=owner.id if owner else None)
    db.session.add(res); db.session.commit()
    rid = res.id
    try:
        name, path = save_upload(f)
        res.filename, res.path = name, path
        text = extract_text(path)
        if len(text.strip()) < 40:
            raise ValueError("No readable text found - the file may be empty, scanned or corrupted")
        data = parse_resume(text)
        cand = owner
        if cand is None:
            dup = Candidate.query.filter_by(email=data["email"]).first() if data["email"] else None
            if dup:
                res.status, res.error, res.candidate_id = "Completed", "Duplicate: matched existing candidate, no new profile created", dup.id
                db.session.commit()
                return res.to_dict(duplicate=True)
            cand = Candidate(source="admin"); db.session.add(cand)
        if owner and data.get("email") and Candidate.query.filter(Candidate.email == data["email"], Candidate.id != owner.id).first():
            data["email"] = None
        apply_data(cand, data, keep_identity=owner is not None)
        db.session.flush()
        res.candidate_id, res.status = cand.id, "Completed"
        db.session.commit()
        try:
            index_candidate(cand)
        except Exception as e:
            print("[index] failed:", e)
        return res.to_dict()
    except Exception as e:
        db.session.rollback()
        res = db.session.get(Resume, rid)
        res.status, res.error = "Failed", str(e)[:290]
        db.session.commit()
        return res.to_dict()
