from flask import Blueprint

from app.utils.api_response import api_response

health_bp = Blueprint("health", __name__)


@health_bp.route("/api", methods=["GET"])
@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return api_response(
        data={
            "status": "ok",
            "service": "Tech Trends Explorer API",
            "endpoints": [
                "/api/language-distribution?since=daily",
                "/api/keywords?since=daily",
                "/api/top-repositories?since=daily",
            ],
        }
    )
