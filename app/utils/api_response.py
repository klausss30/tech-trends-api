from flask import jsonify

def api_response(data=None, code=200, message="success"):
    response = jsonify({
        "code": code,
        "message": message,
        "data": data
    })
    return response, code
