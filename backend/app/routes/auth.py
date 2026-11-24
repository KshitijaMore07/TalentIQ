import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models import User, Candidate
from ..utils.security import current_user

bp = Blueprint("auth", __name__)


@bp.post("/auth/register")
def register():
    d = request.get_json(silent=True) or {}
    name, email, pw = (d.get("name") or "").strip(), (d.get("email") or "").strip().lower(), d.get("password") or ""
    if not name or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify(error="Enter your name and a valid email address"), 400
    if len(pw) < 6:
        return jsonify(error="Password must be at least 6 characters"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="An account with this email already exists"), 409
    u = User(name=name, email=email, role="candidate", password_hash=generate_password_hash(pw))
    db.session.add(u); db.session.flush()
    c = Candidate.query.filter_by(email=email).first()  # claim a profile created from a recruiter upload
    if c and not c.user_id:
        c.user_id = u.id
    elif not c:
        db.session.add(Candidate(user_id=u.id, name=name, email=email, source="self"))
    db.session.commit()
    return jsonify(token=create_access_token(identity=str(u.id)), user=u.to_dict()), 201


@bp.post("/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    u = User.query.filter_by(email=(d.get("email") or "").strip().lower()).first()
    if not u or not check_password_hash(u.password_hash, d.get("password") or ""):
        return jsonify(error="Incorrect email or password"), 401
    return jsonify(token=create_access_token(identity=str(u.id)), user=u.to_dict())


@bp.get("/auth/me")
@jwt_required()
def me():
    return jsonify(user=current_user().to_dict())
