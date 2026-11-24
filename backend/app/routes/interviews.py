from datetime import datetime
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Interview, InterviewFeedback, Application, User, Candidate, Job
from ..services.notify import notify
from ..utils.security import roles, current_user, my_candidate

bp = Blueprint("interviews", __name__)


def body():
    return request.get_json(silent=True) or {}


def when(v):
    return datetime.fromisoformat(str(v).replace("Z", "")[:16])


def cand_user(c):
    return db.session.get(User, c.user_id) if c.user_id else None


@bp.post("/interviews")
@roles("admin")
def schedule():
    d = body()
    try:
        c, j = db.get_or_404(Candidate, d.get("candidate_id")), db.get_or_404(Job, d.get("job_id"))
        iv_user = db.get_or_404(User, d.get("interviewer_id"))
        iv = Interview(candidate_id=c.id, job_id=j.id, interviewer_id=iv_user.id, scheduled_at=when(d.get("scheduled_at")),
                       duration_minutes=int(d.get("duration_minutes") or 45))
    except (ValueError, TypeError):
        return jsonify(error="Pick a valid date and time"), 400
    if iv_user.role != "interviewer":
        return jsonify(error="Choose an interviewer"), 400
    db.session.add(iv)
    a = Application.query.filter_by(candidate_id=c.id, job_id=j.id).first()
    if a:
        a.status = "Interview Scheduled"
    ts = iv.scheduled_at.strftime("%d %b %Y, %H:%M")
    notify(cand_user(c), f"Interview scheduled for {j.title} on {ts} ({iv.duration_minutes} min).", "TalentIQ interview invitation", c.email)
    notify(iv_user, f"You are assigned to interview {c.name} for {j.title} on {ts}.", "TalentIQ interview assignment")
    db.session.commit()
    return jsonify(iv.to_dict()), 201


@bp.get("/interviews")
@roles("admin", "interviewer", "candidate")
def list_interviews():
    u = current_user(); q = Interview.query.order_by(Interview.scheduled_at.desc())
    if u.role == "interviewer":
        q = q.filter_by(interviewer_id=u.id)
    elif u.role == "candidate":
        q = q.filter_by(candidate_id=my_candidate(u).id)
    out = [i.to_dict() for i in q]
    if u.role == "candidate":
        for i in out:
            i.pop("feedback", None)  # feedback is internal
    return jsonify(out)


@bp.put("/interviews/<int:iid>")
@roles("admin")
def update(iid):
    iv = db.get_or_404(Interview, iid); d = body()
    try:
        if d.get("scheduled_at"):
            iv.scheduled_at = when(d["scheduled_at"])
        if d.get("duration_minutes"):
            iv.duration_minutes = int(d["duration_minutes"])
    except (ValueError, TypeError):
        return jsonify(error="Pick a valid date and time"), 400
    if d.get("status") in ("Scheduled", "Cancelled"):
        iv.status = d["status"]
    verb = "cancelled" if iv.status == "Cancelled" else f"rescheduled to {iv.scheduled_at.strftime('%d %b %Y, %H:%M')}"
    msg = f"Your interview for {iv.job.title} has been {verb}."
    notify(cand_user(iv.candidate), msg, "TalentIQ interview update", iv.candidate.email)
    notify(iv.interviewer, f"Interview with {iv.candidate.name} has been {verb}.")
    db.session.commit()
    return jsonify(iv.to_dict())


@bp.post("/interviews/<int:iid>/feedback")
@roles("interviewer")
def feedback(iid):
    iv = db.get_or_404(Interview, iid)
    if iv.interviewer_id != current_user().id:
        return jsonify(error="Access denied"), 403
    d = body()
    try:
        scores = [int(d.get(k)) for k in ("technical", "communication", "problem_solving")]
    except (TypeError, ValueError):
        return jsonify(error="Rate all three skills from 1 to 10"), 400
    if any(s < 1 or s > 10 for s in scores):
        return jsonify(error="Ratings must be between 1 and 10"), 400
    fb = iv.feedback or InterviewFeedback(interview_id=iv.id)
    fb.technical, fb.communication, fb.problem_solving = scores
    fb.remarks, fb.recommendation = d.get("remarks"), d.get("recommendation") or "Maybe"
    iv.status = "Completed"
    db.session.add(fb); db.session.commit()
    return jsonify(iv.to_dict())
