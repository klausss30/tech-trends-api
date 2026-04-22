import logging
from contextlib import closing

from flask import Blueprint, request

from app.db import get_connection
from app.utils.api_response import api_response
from app.utils.request_args import validate_since

language_bp = Blueprint("language", __name__)

@language_bp.route("/api/language-distribution", methods=["GET"])
def get_language_distribution():
    since = request.args.get("since", "daily")
    validation_error = validate_since(since)
    if validation_error:
        return validation_error

    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("""
                    SELECT language, language_color, COUNT(*) as count
                    FROM trending_repositories
                    WHERE time_span = %s
                    GROUP BY language, language_color
                    ORDER BY count DESC
                """, (since,))
                rows = cur.fetchall()

        results = [
            {
                "language": r[0],
                "color": r[1],
                "count": r[2]
            } for r in rows if r[0]
        ]

        return api_response(data=results)

    except Exception:
        logging.exception("Failed to fetch language distribution")
        return api_response(code=500, message="Internal server error", data=[])
