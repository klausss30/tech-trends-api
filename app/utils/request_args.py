from app.utils.api_response import api_response


ALLOWED_SINCE_VALUES = {"daily", "weekly", "monthly"}


def validate_since(value):
    if value in ALLOWED_SINCE_VALUES:
        return None

    allowed = ", ".join(sorted(ALLOWED_SINCE_VALUES))
    return api_response(
        code=400,
        message=f"Invalid since value. Use one of: {allowed}.",
        data=[],
    )
