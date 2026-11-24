def register_routes(app):
    from .auth import bp as auth
    from .candidate import bp as candidate
    from .admin import bp as admin
    from .interviews import bp as interviews
    for b in (auth, candidate, admin, interviews):
        app.register_blueprint(b, url_prefix="/api")
