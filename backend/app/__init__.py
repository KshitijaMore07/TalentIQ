import os, json
from flask import Flask, jsonify
from werkzeug.security import generate_password_hash
from .extensions import db, jwt, cors


def create_app():
    from config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    for sub in ("resumes", "temp"):
        os.makedirs(os.path.join(Config.UPLOAD_DIR, sub), exist_ok=True)
    db.init_app(app); jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    from .routes import register_routes
    register_routes(app)

    @app.errorhandler(413)
    def too_big(_): return jsonify(error="File too large"), 413

    @app.get("/api/health")
    def health(): return jsonify(status="ok", app="TalentIQ")

    with app.app_context():
        from . import models  # noqa
        db.create_all()
        seed()
    return app


def seed():
    from .models import User, Job
    if not User.query.filter_by(role="admin").first():
        db.session.add(User(name="Admin Recruiter", email="admin@talentiq.com", role="admin",
                            password_hash=generate_password_hash("Admin@123")))
        db.session.add(User(name="Ravi Interviewer", email="interviewer@talentiq.com", role="interviewer",
                            password_hash=generate_password_hash("Interview@123")))
    if not Job.query.first():
        db.session.add(Job(title="Python Backend Developer", location="Pune", employment_type="Full-time", education="Bachelor",
                           description="Build REST APIs with Flask, design MySQL schemas and ship reliable services.",
                           required_skills=json.dumps(["Python", "Flask", "SQL"]), preferred_skills=json.dumps(["Docker", "AWS", "Git"]),
                           min_experience=1, max_experience=5, deadline="2026-12-31"))
        db.session.add(Job(title="Machine Learning Engineer", location="Remote", employment_type="Full-time", education="Master",
                           description="Develop NLP and semantic search models, embeddings and LLM powered features.",
                           required_skills=json.dumps(["Python", "Machine Learning", "NLP"]), preferred_skills=json.dumps(["PyTorch", "LLM", "SQL"]),
                           min_experience=2, max_experience=6, deadline="2026-12-31"))
    db.session.commit()
