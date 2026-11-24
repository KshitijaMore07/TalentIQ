import json
from datetime import datetime
from ..extensions import db


def jl(v):
    try:
        return json.loads(v) if v else []
    except Exception:
        return []


def iso(d):
    return d.isoformat() if d else None


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="candidate")  # candidate | admin | interviewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(id=self.id, name=self.name, email=self.email, role=self.role)


class Candidate(db.Model):
    __tablename__ = "candidates"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    name = db.Column(db.String(160))
    email = db.Column(db.String(160), unique=True)
    phone = db.Column(db.String(40))
    location = db.Column(db.String(120))
    summary = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    projects = db.Column(db.Text)
    experience_years = db.Column(db.Float, default=0)
    source = db.Column(db.String(20), default="self")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.relationship("CandidateSkill", backref="candidate", cascade="all, delete-orphan")

    def skill_list(self):
        return [s.skill for s in self.skills]

    def to_dict(self):
        return dict(id=self.id, name=self.name, email=self.email, phone=self.phone, location=self.location,
                    summary=self.summary, education=jl(self.education), experience=jl(self.experience),
                    projects=jl(self.projects), experience_years=self.experience_years or 0,
                    skills=self.skill_list(), source=self.source, created_at=iso(self.created_at))


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=True)
    filename = db.Column(db.String(255))
    path = db.Column(db.String(400))
    status = db.Column(db.String(20), default="Processing")  # Processing | Completed | Failed
    error = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, duplicate=False):
        c = db.session.get(Candidate, self.candidate_id) if self.candidate_id else None
        return dict(id=self.id, filename=self.filename, status=self.status, error=self.error, duplicate=duplicate,
                    candidate_id=self.candidate_id, candidate_name=c.name if c else None, created_at=iso(self.created_at))


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    preferred_skills = db.Column(db.Text)
    min_experience = db.Column(db.Float, default=0)
    max_experience = db.Column(db.Float, default=0)
    education = db.Column(db.String(160))
    location = db.Column(db.String(120))
    employment_type = db.Column(db.String(40), default="Full-time")
    deadline = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(id=self.id, title=self.title, description=self.description, required_skills=jl(self.required_skills),
                    preferred_skills=jl(self.preferred_skills), min_experience=self.min_experience or 0,
                    max_experience=self.max_experience or 0, education=self.education, location=self.location,
                    employment_type=self.employment_type, deadline=self.deadline, status=self.status)


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(db.String(30), default="Applied")  # Applied|Shortlisted|Approved|Interview Scheduled|Selected|Rejected
    match_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("candidate_id", "job_id"),)
    candidate = db.relationship("Candidate")
    job = db.relationship("Job")

    def to_dict(self):
        return dict(id=self.id, candidate_id=self.candidate_id, candidate_name=self.candidate.name, job_id=self.job_id,
                    job_title=self.job.title, status=self.status, match_score=self.match_score, created_at=iso(self.created_at))


class CandidateSkill(db.Model):
    __tablename__ = "candidate_skills"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    skill = db.Column(db.String(100), nullable=False)


class CandidateEmbedding(db.Model):
    __tablename__ = "candidate_embeddings"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), unique=True)
    vector_id = db.Column(db.String(60))
    model = db.Column(db.String(80))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Shortlist(db.Model):
    __tablename__ = "shortlists"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("job_id", "candidate_id"),)


class InternalNote(db.Model):
    __tablename__ = "internal_notes"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        a = db.session.get(User, self.author_id)
        return dict(id=self.id, note=self.note, author=a.name if a else "", created_at=iso(self.created_at))


class Interview(db.Model):
    __tablename__ = "interviews"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    interviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=45)
    status = db.Column(db.String(20), default="Scheduled")  # Scheduled | Cancelled | Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidate = db.relationship("Candidate")
    job = db.relationship("Job")
    interviewer = db.relationship("User")
    feedback = db.relationship("InterviewFeedback", backref="interview", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return dict(id=self.id, candidate_id=self.candidate_id, candidate_name=self.candidate.name, job_id=self.job_id,
                    job_title=self.job.title, interviewer_id=self.interviewer_id, interviewer_name=self.interviewer.name,
                    scheduled_at=iso(self.scheduled_at), duration_minutes=self.duration_minutes, status=self.status,
                    feedback=self.feedback.to_dict() if self.feedback else None)


class InterviewFeedback(db.Model):
    __tablename__ = "interview_feedback"
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id"), unique=True, nullable=False)
    technical = db.Column(db.Integer)
    communication = db.Column(db.Integer)
    problem_solving = db.Column(db.Integer)
    remarks = db.Column(db.Text)
    recommendation = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(technical=self.technical, communication=self.communication, problem_solving=self.problem_solving,
                    remarks=self.remarks, recommendation=self.recommendation, created_at=iso(self.created_at))


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(400), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(id=self.id, message=self.message, created_at=iso(self.created_at))
