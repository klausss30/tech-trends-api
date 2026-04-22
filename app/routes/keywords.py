import logging
import re
from collections import Counter
from contextlib import closing

from flask import Blueprint, request

from app.db import get_connection
from app.utils.api_response import api_response
from app.utils.request_args import validate_since
from app.utils.stopwords import stop_words

keywords_bp = Blueprint("keywords", __name__)

@keywords_bp.route("/api/keywords", methods=["GET"])
def get_keywords():
    since = request.args.get("since", "daily")
    validation_error = validate_since(since)
    if validation_error:
        return validation_error

    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("""
                    SELECT description
                    FROM trending_repositories
                    WHERE time_span = %s
                """, (since,))
                rows = cur.fetchall()

        all_text = " ".join([r[0] for r in rows if r[0]])
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())

        filtered_words = [w for w in words if w not in stop_words]
        common = Counter(filtered_words).most_common(30)

        results = [{"keyword": w, "weight": c} for w, c in common]

        return api_response(data=results)

    except Exception:
        logging.exception("Failed to fetch keywords")
        return api_response(code=500, message="Internal server error", data=[])
