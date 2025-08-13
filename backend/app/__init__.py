from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging
    if not app.debug:
        gunicorn_error_handlers = logging.getLogger("gunicorn.error")
        if gunicorn_error_handlers.handlers:
            app.logger.handlers = gunicorn_error_handlers.handlers
            app.logger.setLevel(gunicorn_error_handlers.level)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS
    origins = app.config.get("CORS_ORIGINS", ["*"])
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    # Blueprints
    from .routes.health import bp as health_bp
    from .routes.auth import bp as auth_bp
    from .routes.hotels import bp as hotels_bp
    from .routes.bookings import bp as bookings_bp
    from .routes.admin import bp as admin_bp
    from .routes.me import bp as me_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(hotels_bp, url_prefix="/api")
    app.register_blueprint(bookings_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(me_bp, url_prefix="/api")

    # Error handlers -> JSON as default
    @app.errorhandler(404)
    def _404(_e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def _400(e):
        return jsonify({"error": "Bad request", "detail": str(e)}), 400

    @app.errorhandler(500)
    def _500(e):
        app.logger.exception("Server error: %s", e)
        return jsonify({"error": "Internal server error"}), 500

    return app
