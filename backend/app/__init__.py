from flask import Flask
from app.extensions.extensions import db, migrate, bcrypt, cors
from app.config.app_config import AppConfig
from app.apis.auth.resource import auth
from app.apis.settings.resource import settings
def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Configure CORS to allow requests from specified origins
    cors.init_app(
        app,
        resources={r"/*": {
            "origins": app.config.get("CORS_ORIGINS", ["http://localhost:3000"]),
            "methods": app.config.get("CORS_METHODS", ["GET", "POST", "PUT", "DELETE", "OPTIONS"]),
            "allow_headers": app.config.get("CORS_ALLOW_HEADERS", ["Content-Type", "Authorization"]),
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "send_wildcard": False,
            "vary_header": True
        }}
    )

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    app.register_blueprint(auth)
    app.register_blueprint(settings)

    with app.app_context():
        db.create_all()
    return app