from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Candidate, Application, Job, Interview, InternalNote, Notification
from ..services.pipeline import process_resume, apply_data
from ..services.embeddings import index_candidate, similarities
from ..services.matching import job_text, score_candidate
from ..utils.security import roles, current_user, my_candidate

bp = Blueprint("candidate", __name__)


def _reindex(c):
    try:
        index_candidate(c)
    except Exception as e:
        print("[index] failed:", e)


@bp.get("/candidates/profile")
@roles("candidate")
def profile():
    return jsonify(my_candidate(current_user()).to_dict())


@bp.put("/candidates/profile")
@roles("candidate")
def update_profile():
    c = my_candidate(current_user())
    apply_data(c, request.get_json(silent=True) or {}, keep_identity=True)
    db.session.commit(); _reindex(c)
    return jsonify(c.to_dict())


@bp.get("/candidates/<int:cid>")
@roles("candidate", "admin", "interviewer")
def get_candidate(cid):
    u = current_user()
    c = db.get_or_404(Candidate, cid)
    if u.role == "candidate" and c.user_id != u.id:
        return jsonify(error="Access denied"), 403
    if u.role == "interviewer" and not Interview.query.filter_by(candidate_id=cid, interviewer_id=u.id).first():
        return jsonify(error="Access denied"), 403
    d = c.to_dict()
    if u.role == "admin":
        d["notes"] = [n.to_dict() for n in InternalNote.query.filter_by(candidate_id=cid).order_by(InternalNote.id.desc())]
    return jsonify(d)


@bp.post("/resumes/upload")
@roles("candidate")
def upload_resume():
    f = request.files.get("file")
    if not f:
        return jsonify(error="Choose a PDF or DOCX file"), 400
    r = process_resume(f, owner=my_candidate(current_user()))
    return jsonify(result=r, profile=my_candidate(current_user()).to_dict()), (200 if r["status"] == "Completed" else 422)


@bp.get("/applications/mine")
@roles("candidate")
def my_apps():
    c = my_candidate(current_user())
    return jsonify([a.to_dict() for a in Application.query.filter_by(candidate_id=c.id).order_by(Application.id.desc())])


@bp.post("/applications")
@roles("candidate")
def apply():
    c = my_candidate(current_user())
    job = db.get_or_404(Job, (request.get_json(silent=True) or {}).get("job_id"))
    if job.status != "Open":
        return jsonify(error="This job is closed"), 400
    if Application.query.filter_by(candidate_id=c.id, job_id=job.id).first():
        return jsonify(error="You have already applied"), 409
    a = Application(candidate_id=c.id, job_id=job.id)
    try:
        a.match_score = score_candidate(c, job, similarities(job_text(job)).get(c.id, 0))["score"]
    except Exception as e:
        print("[apply] scoring skipped:", e)
    db.session.add(a); db.session.commit()
    return jsonify(a.to_dict()), 201


@bp.get("/notifications")
@jwt_required()
def notifications():
    q = Notification.query.filter_by(user_id=current_user().id).order_by(Notification.id.desc()).limit(50)
    return jsonify([n.to_dict() for n in q])
