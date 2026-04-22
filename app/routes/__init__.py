from flask import Blueprint
from app.routes.health import health_bp
from app.routes.popular import popular_bp
from app.routes.language import language_bp
from app.routes.keywords import keywords_bp

bp = Blueprint("api", __name__)
bp.register_blueprint(health_bp)
bp.register_blueprint(popular_bp)
bp.register_blueprint(language_bp)
bp.register_blueprint(keywords_bp)
