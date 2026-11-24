import csv, io, json
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from ..extensions import db
from ..models import (User, Candidate, Resume, Job, Application, Shortlist, InternalNote, Interview, CandidateSkill)
from ..services.pipeline import process_resume, apply_data, clean_list
from ..services.embeddings import index_candidate, similarities, reset_index
from ..services.matching import job_text, score_candidate
from ..services.notify import notify
from ..utils.security import roles, current_user

bp = Blueprint("admin", __name__)
STATUSES = ("Applied", "Shortlisted", "Approved", "Interview Scheduled", "Selected", "Rejected")


def body():
    return request.get_json(silent=True) or {}


@bp.get("/admin/stats")
@roles("admin")
def stats():
    by = dict(db.session.query(Application.status, func.count(Application.id)).group_by(Application.status).all())
    return jsonify(candidates=Candidate.query.count(), resumes=Resume.query.count(), active_jobs=Job.query.filter_by(status="Open").count(),
                   applications=Application.query.count(), shortlisted=Shortlist.query.count(),
                   scheduled_interviews=Interview.query.filter_by(status="Scheduled").count(),
                   selected=Application.query.filter_by(status="Selected").count(), by_status={s: by.get(s, 0) for s in STATUSES})


# ---------- jobs ----------
def fill_job(j, d):
    for k in ("title", "description", "education", "location", "employment_type", "deadline", "status"):
        if k in d:
            setattr(j, k, d[k])
    for k in ("required_skills", "preferred_skills"):
        if k in d:
            setattr(j, k, json.dumps(clean_list(d[k])))
    for k in ("min_experience", "max_experience"):
        if k in d:
            setattr(j, k, float(d[k] or 0))


@bp.get("/jobs")
@jwt_required()
def jobs():
    q = Job.query.order_by(Job.id.desc())
    if current_user().role != "admin":
        q = q.filter_by(status="Open")
    return jsonify([j.to_dict() for j in q])


@bp.post("/jobs")
@roles("admin")
def create_job():
    d = body()
    if not (d.get("title") or "").strip():
        return jsonify(error="Job title is required"), 400
    j = Job(); fill_job(j, d); db.session.add(j); db.session.commit()
    return jsonify(j.to_dict()), 201


@bp.get("/jobs/<int:jid>")
@jwt_required()
def get_job(jid):
    return jsonify(db.get_or_404(Job, jid).to_dict())


@bp.put("/jobs/<int:jid>")
@roles("admin")
def update_job(jid):
    j = db.get_or_404(Job, jid); fill_job(j, body()); db.session.commit()
    return jsonify(j.to_dict())


@bp.delete("/jobs/<int:jid>")
@roles("admin")
def delete_job(jid):
    j = db.get_or_404(Job, jid)
    for m in (Shortlist, Application, Interview):
        for r in m.query.filter_by(job_id=jid):
            db.session.delete(r)
    db.session.delete(j); db.session.commit()
    return jsonify(ok=True)


# ---------- resumes & candidates ----------
@bp.post("/resumes/bulk-upload")
@roles("admin")
def bulk_upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify(error="Choose one or more resumes"), 400
    return jsonify([process_resume(f) for f in files])


@bp.get("/admin/resumes")
@roles("admin")
def resumes():
    return jsonify([r.to_dict() for r in Resume.query.order_by(Resume.id.desc()).limit(100)])


@bp.get("/admin/candidates")
@roles("admin")
def candidates():
    q, skill = (request.args.get("q") or "").strip().lower(), (request.args.get("skill") or "").strip().lower()
    out = []
    for c in Candidate.query.order_by(Candidate.id.desc()):
        if q and q not in f"{c.name} {c.email} {c.location}".lower():
            continue
        if skill and not any(skill in s.lower() for s in c.skill_list()):
            continue
        out.append(c.to_dict())
    return jsonify(out)


@bp.put("/admin/candidates/<int:cid>")
@roles("admin")
def edit_candidate(cid):
    c = db.get_or_404(Candidate, cid)
    apply_data(c, body(), keep_identity=True)
    db.session.commit()
    try:
        index_candidate(c)
    except Exception as e:
        print("[index] failed:", e)
    return jsonify(c.to_dict())


@bp.post("/admin/candidates/<int:cid>/notes")
@roles("admin")
def add_note(cid):
    db.get_or_404(Candidate, cid)
    t = (body().get("note") or "").strip()
    if not t:
        return jsonify(error="Write a note first"), 400
    n = InternalNote(candidate_id=cid, author_id=current_user().id, note=t); db.session.add(n); db.session.commit()
    return jsonify(n.to_dict()), 201


@bp.post("/admin/reindex")
@roles("admin")
def reindex():
    reset_index()
    for c in Candidate.query:
        index_candidate(c)
    return jsonify(ok=True, count=Candidate.query.count())


@bp.get("/admin/interviewers")
@roles("admin")
def interviewers():
    return jsonify([u.to_dict() for u in User.query.filter_by(role="interviewer")])


@bp.post("/admin/interviewers")
@roles("admin")
def add_interviewer():
    d = body(); email = (d.get("email") or "").strip().lower()
    if not d.get("name") or not email or len(d.get("password") or "") < 6:
        return jsonify(error="Name, email and a 6+ character password are required"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already in use"), 409
    u = User(name=d["name"], email=email, role="interviewer", password_hash=generate_password_hash(d["password"]))
    db.session.add(u); db.session.commit()
    return jsonify(u.to_dict()), 201


# ---------- matching & search ----------
@bp.get("/matching/<int:jid>")
@roles("admin")
def matching(jid):
    job = db.get_or_404(Job, jid)
    sims = similarities(job_text(job))
    short = {s.candidate_id for s in Shortlist.query.filter_by(job_id=jid)}
    apps = {a.candidate_id: a for a in Application.query.filter_by(job_id=jid)}
    out = []
    for c in Candidate.query:
        r = score_candidate(c, job, sims.get(c.id, 0))
        r["shortlisted"], r["applied"] = c.id in short, c.id in apps
        if c.id in apps:
            apps[c.id].match_score = r["score"]
        out.append(r)
    db.session.commit()
    return jsonify(job=job.to_dict(), results=sorted(out, key=lambda x: -x["score"]))


@bp.post("/search")
@roles("admin")
def search():
    d = body(); q = (d.get("query") or "").strip()
    if not q:
        return jsonify(error="Describe the candidate you are looking for"), 400
    sims = similarities(q, n=int(d.get("limit") or 10))
    if not sims:  # empty index: keyword fallback
        words = [w for w in q.lower().split() if len(w) > 2]
        sims = {c.id: 0.3 for c in Candidate.query if any(w in (" ".join(c.skill_list()) + (c.summary or "")).lower() for w in words)}
    out = []
    for cid, s in sorted(sims.items(), key=lambda x: -x[1]):
        c = db.session.get(Candidate, cid)
        if c:
            out.append(dict(c.to_dict(), similarity=round(min(100, max(0, (s - 0.10) / 0.55 * 100))), raw=round(s, 3)))
    return jsonify(out)


# ---------- shortlists & applications ----------
def get_app(cid, jid):
    a = Application.query.filter_by(candidate_id=cid, job_id=jid).first()
    if not a:
        a = Application(candidate_id=cid, job_id=jid); db.session.add(a); db.session.flush()
    return a


@bp.post("/shortlists")
@roles("admin")
def shortlist():
    d = body(); jid = d.get("job_id"); db.get_or_404(Job, jid); added = 0
    for cid in d.get("candidate_ids") or []:
        if not db.session.get(Candidate, cid):
            continue
        if not Shortlist.query.filter_by(job_id=jid, candidate_id=cid).first():
            db.session.add(Shortlist(job_id=jid, candidate_id=cid)); added += 1
        a = get_app(cid, jid)
        if a.status == "Applied":
            a.status = "Shortlisted"
    db.session.commit()
    return jsonify(added=added)


@bp.get("/shortlists")
@roles("admin")
def get_shortlist():
    jid = request.args.get("job_id", type=int)
    out = []
    for s in Shortlist.query.filter_by(job_id=jid):
        a = get_app(s.candidate_id, jid)
        c = db.session.get(Candidate, s.candidate_id)
        out.append(dict(application_id=a.id, status=a.status, match_score=a.match_score, candidate=c.to_dict()))
    db.session.commit()
    return jsonify(out)


@bp.delete("/shortlists")
@roles("admin")
def unshortlist():
    s = Shortlist.query.filter_by(job_id=request.args.get("job_id", type=int), candidate_id=request.args.get("candidate_id", type=int)).first()
    if s:
        db.session.delete(s); db.session.commit()
    return jsonify(ok=True)


@bp.get("/shortlists/export")
@roles("admin")
def export():
    jid = request.args.get("job_id", type=int)
    job = db.get_or_404(Job, jid)
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["Name", "Email", "Phone", "Experience (yrs)", "Skills", "Status", "Match score"])
    for s in Shortlist.query.filter_by(job_id=jid):
        c = db.session.get(Candidate, s.candidate_id); a = get_app(c.id, jid)
        w.writerow([c.name, c.email, c.phone, c.experience_years, "; ".join(c.skill_list()), a.status, a.match_score])
    db.session.commit()
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=shortlist_{job.id}.csv"})


@bp.put("/applications/<int:aid>")
@roles("admin")
def set_status(aid):
    a = db.get_or_404(Application, aid)
    st = body().get("status")
    if st not in STATUSES:
        return jsonify(error="Unknown status"), 400
    a.status = st
    cu = a.candidate.user_id and db.session.get(User, a.candidate.user_id)
    msgs = {"Approved": f"Good news: you are approved for an interview for {a.job.title}. We will send the schedule soon.",
            "Selected": f"Congratulations! You have been selected for {a.job.title}.",
            "Rejected": f"Thank you for applying to {a.job.title}. We will not move forward at this time."}
    if st in msgs:
        notify(cu or None, msgs[st], f"TalentIQ: {a.job.title}", to_email=a.candidate.email)
    db.session.commit()
    return jsonify(a.to_dict())
