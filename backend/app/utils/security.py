from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..extensions import db
from ..models import User, Candidate


def current_user():
    return db.session.get(User, int(get_jwt_identity()))


def my_candidate(user):
    return Candidate.query.filter_by(user_id=user.id).first()


def roles(*allowed):
    def deco(fn):
        @wraps(fn)
        def wrap(*a, **k):
            verify_jwt_in_request()
            u = current_user()
            if not u or u.role not in allowed:
                return jsonify(error="Access denied"), 403
            return fn(*a, **k)
        return wrap
    return deco
