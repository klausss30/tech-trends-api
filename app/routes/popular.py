import logging
from contextlib import closing

from flask import Blueprint, request

from app.db import get_connection
from app.utils.api_response import api_response
from app.utils.request_args import validate_since

popular_bp = Blueprint("popular", __name__)

@popular_bp.route("/api/top-repositories", methods=["GET"])
def get_top_repositories():
    since = request.args.get("since", "daily")
    validation_error = validate_since(since)
    if validation_error:
        return validation_error

    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("""
                    SELECT repo_name, repo_url, description, language, stars_total
                    FROM (
                        SELECT repo_name, repo_url, description, language, stars_total,
                               ROW_NUMBER() OVER (PARTITION BY repo_name ORDER BY stars_total DESC) as rn
                        FROM trending_repositories
                        WHERE time_span = %s
                    ) t
                    WHERE rn = 1
                    ORDER BY stars_total DESC
                """, (since,))
                rows = cur.fetchall()

        results = [
            {
                "repo_name": r[0],
                "repo_url": r[1],
                "description": r[2],
                "language": r[3],
                "stars": r[4]
            } for r in rows
        ]

        return api_response(data=results)

    except Exception:
        logging.exception("Failed to fetch top repositories")
        return api_response(code=500, message="Internal server error", data=[])
