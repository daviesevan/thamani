from flask import Flask, request
from app.extensions.extensions import db, migrate, bcrypt, cors, mail
from app.config.app_config import AppConfig
from app.apis.auth.resource import auth
from app.apis.settings.resource import settings
from app.apis.tracking.resource import tracking
from app.apis.products.resource import products
from app.apis.scraping.resource import scraping
from app.apis.real_scraping.resource import real_scraping
from app.apis.wishlist.resource import wishlist

# Import models to register them with SQLAlchemy
from app.models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Configure CORS to allow requests from specified origins
    cors.init_app(
        app,
        resources={r"/*": {
            "origins": app.config.get("CORS_ORIGINS", ["http://localhost:3000", "http://localhost:3001"]),
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
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://localhost:3001']:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(settings, url_prefix='/settings')
    app.register_blueprint(tracking, url_prefix='/tracking')
    app.register_blueprint(products, url_prefix='/products')
    app.register_blueprint(scraping, url_prefix='/scraping')
    app.register_blueprint(real_scraping, url_prefix='/real-scraping')
    app.register_blueprint(wishlist, url_prefix='/wishlist')

    with app.app_context():
        db.create_all()
    return app